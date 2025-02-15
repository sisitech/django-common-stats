import sys
from django.conf import settings
from django.db.models import Count, F
from httpx import request
from mylib.my_common import str2bool
import time

# Create your views here.
from drf_autodocs.decorators import format_docstring
from rest_framework import generics
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import hashlib

from mylib.my_common import (
    MyCustomException,
    MyDjangoFilterBackend,
    MyStandardPagination,
    FilterBasedOnRole,
)
from stats.models import Export
from stats.serializers import BaseDynamicStatsSerializer
from stats.tasks import export_students_reports
from django.core.cache import cache

# from stats.utils  as utils
import stats.utils as stat_utils


class OptimizedExportTriggerAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Trigger Export
        xp = Export(
            name="Export Students",
            title="Onekana Report June",
            custom_report_name="overall",
            is_custom=True,
        )
        xp.save()
        # export_students(xp.id, verbose_name=xp.name, creator=xp)
        # notify_user(user.id, verbose_name="Notify user", creator=user)
        return Response({"id": xp.id, "name": xp.name, "status": xp.get_status_display()})


class CursorSetPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "page_size"
    ordering = "-value"


class MyCustomDyamicStats(FilterBasedOnRole):
    count_name = "count"
    count_field="id"
    pagination_class = MyStandardPagination
    pagination_class = CursorSetPagination
    stats_definitions = None
    should_export = False
    default_fields = {}

    def get_stats_cache_key(self, suffix_key=""):
        key = self.request.get_raw_uri()
        user_id = 0
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
        final_key = f"{key}_{user_id}_{suffix_key}"
        result = hashlib.md5(final_key.encode()).hexdigest()
        return result

    def get_key_duration(self, key):
        return f"{key}_duration"

    def set_cache_data(self, key, data, duration_secs=None):
        duration = 60
        if hasattr(settings, "CACHE_TIMEOUT"):
            duration = settings.CACHE_TIMEOUT
        if duration_secs != None:
            duration = int(duration_secs)
        # print(f"duration ", duration,"dura_sec ",duration_secs)
        cache.set(self.get_key_duration(key), duration, timeout=duration + 3)
        cache.set(key, data, timeout=duration, version=1)

    def check_if_cache_enabled(self):
        return True

    def get_cache_data(self, key):
        data = cache.get(key)
        if data == None:
            return data
        timeout = cache.get(self.get_key_duration(key))
        data["cache"] = True
        data["cache_timeout"] = timeout
        return data

    def list(self, request, *args, **kwargs):
        self.stat_type = self.get_current_stat_type()
        if self.stat_type not in self.stats_definitions:
            raise MyCustomException("Supported types are: {}".format(",".join(self.stats_definitions)))
        export = True if self.request.query_params.get("export") == "true" else False
        ignore_cache = True if self.request.query_params.get("ignore_cache") == "true" else False
        cache_timeout = self.request.query_params.get("cache_timeout", None)

        # Check if cache enabled
        cache_key = self.get_stats_cache_key()

        if not export:
            data = self.get_cache_data(cache_key)
            if ignore_cache:
                pass
            elif data != None:
                print("CACHE HIT")
                return Response(data)

        self.should_export = export
        queryset = self.filter_queryset(self.get_queryset())

        ## Filter based on definitions
        enabled_filters = stat_utils.get_enabled_filters(
            self.stats_definitions,
            self.stat_type,
            self.get_utils_kwargs(),
            query_params=self.request.query_params,
        )

        queryset = self.get_my_queryset(queryset)

        ## Custom filtering

        queryset = self.get_grouped_by_data(queryset)

        # print(enabled_filters)
        if enabled_filters:
            ## Override with filters from enabled filters
            queryset = queryset.filter(**enabled_filters)

        paginator = self.request.query_params.get("paginator", "standard")

        ## Global filters

        if paginator == "cursor":
            self.pagination_class = CursorSetPagination
        else:
            self.pagination_class = MyStandardPagination

        if self.pagination_class == CursorSetPagination:
            if self.stat_type == "id":
                setattr(self.pagination_class, "ordering", "id")
            else:
                setattr(self.pagination_class, "ordering", "value")

        descriptions = request.query_params.get("descriptions", "")
        try:
            # parsedDescriptions=list(map(lambda x:{"field":x.split("*")[0],"value":x.split("*")[1]},descriptions.split("-")))
            parsedDescriptions = descriptions.replace("-", ", ").replace("*", "=")
        except Exception as e:
            print(e)
            parsedDescriptions = ["Failed to parse"]

        # print("descriptions",parsedDescriptions)

        # print(queryset.query)
        if export:
            queryset_count = queryset.count()
            if queryset_count < 1:
                raise MyCustomException("No records found.", 400)

            xp = Export.objects.create(
                name="Export {}s by {}".format(self.get_model_name(), self.get_stat_type_name()),
                args=parsedDescriptions,
                user_id=self.request.user.id,
            )

            headers = self.get_headers(queryset.first())
            filters = self.get_possible_filters()

            query_params = self.request.query_params
            self.schedule_export_task(query_params=query_params, headers=headers, filters=filters, export=xp)

            return Response(
                {"id": xp.id, "name": xp.name, "status": xp.get_status_display()},
                status=201,
            )

        page = self.paginate_queryset(queryset)
        ##Introduce some sort of formatting
        if page is not None:
            # serializer = self.get_serializer(page, many=True)
            # print("page",page)
            resp_data_res = self.get_paginated_response(page)
            resp_data = resp_data_res.data
            # resp_data["cache"]=True
            self.set_cache_data(cache_key, resp_data, duration_secs=cache_timeout)
            return resp_data_res

        # serializer = self.get_serializer(queryset, many=True)
        resp_data = list(queryset)
        # print(resp_data)
        self.set_cache_data(cache_key, resp_data, duration_secs=cache_timeout)
        return Response(resp_data)

    def get_export_task_user(self):
        return self.request.user.id

    def schedule_export_task(self, query_params={}, headers=[], filters={}, export=None):
        if "test" in sys.argv:
            export_students_reports.task_function(
                export.id,
                user_id=self.get_export_task_user(),
                verbose_name=export.name,
                model_name=self.get_model_name(),
                app_name=self.get_model_app_name(),
                count_name=self.count_name,
                query_params=query_params,
                stat_type=self.stat_type,
                headers=headers,
                filters=filters,
                export=self.should_export,
                creator=export,
            )
        else:
            export_students_reports(
                export.id,
                user_id=self.get_export_task_user(),
                verbose_name=export.name,
                model_name=self.get_model_name(),
                app_name=self.get_model_app_name(),
                count_name=self.count_name,
                query_params=query_params,
                stat_type=self.stat_type,
                headers=headers,
                export=self.should_export,
                filters=filters,
                creator=export,
            )

    def get_current_stat_type(self):
        stat_type = self.kwargs.get("type", None)
        if stat_type is None:
            return "id"
        return self.kwargs.get("type").replace("/", "")

    def get_model_name(self):
        model = self.queryset.model
        return model._meta.object_name

    def get_model_app_name(self):
        model = self.queryset.model
        return model._meta.app_label

    def get_stat_type_name(self):
        return self.stat_type.replace("-", " ").title()

    def get_filter_class(self):
        return MyDjangoFilterBackend().get_filterset(self.request, self.queryset, self)

    def get_filters_options(self):
        fclass = self.get_filter_class()
        filters = {ft.field_name: {"lookup_expr": ft.lookup_expr} for key, ft in fclass.get_filters().items()}
        return filters

    def get_possible_filters(self):
        filters = self.get_filter_class().get_filters()
        options = {
            fp.field_name: {
                "lookup_expr": fp.lookup_expr,
                "value": self.get_filter_value(key, fp),
            }
            for key, fp in filters.items()
            if key in self.request.query_params
        }
        return options

    def get_filter_value(self, key, filter):
        # print(filter.__class__.__name__)
        filter_type_name = filter.__class__.__name__
        value = self.request.query_params.get(key)
        if filter_type_name == "BooleanFilter":
            value = str2bool(value)
        return value

    def get_serializer_class(self):
        return self.serializer_class

    def get_headers(self, row):
        return [{"name": self.get_header_title(value), "value": value} for value in row]

    def get_header_title(self, name):
        if name == "value":
            return self.stat_type.title()
        return name.replace("_", " ").title()

    def get_my_queryset(self, queryset):
        return queryset

    def get_fields(self):
        return {
            self.count_name: Count(
                self.count_field,
            )
        }

    def get_utils_kwargs(self):
        return {
            "export": True if self.request.query_params.get("export") == "true" else False,
            "count_name": self.count_name,
            "query_params": self.request.query_params,
            "stat_type": self.stat_type,
            "default_fields": self.default_fields,
            "app_name": self.get_model_app_name(),
            "model_name": self.get_model_name(),
            "array_query_params": self.request.GET,
            "count_field":self.count_field,
        }

    def get_grouped_by_data(self, queryset):
        kwargs = self.get_utils_kwargs()
        att = stat_utils.get_grouped_by_data(queryset, self.stats_definitions, kwargs)
        return stat_utils.my_order_by(att, kwargs)
