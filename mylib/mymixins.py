from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.utils import timezone
from mylib.my_common import MyCustomException, MyDjangoFilterBackend, MyIsAuthenticatedOrOptions
from mylib.queryset2excel import exportcsv
from mylib.my_common import CursorSetPagination, FilterBasedOnRole, MyCustomException, MyDjangoFilterBackend, MyIsAuthenticatedOrOptions, MyStandardPagination
import mylib.utils as stat_utils
from django.db.models import Count

from stats.models import Export
from stats.tasks import export_students_reports


class MyViewMixin(object):
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (MyIsAuthenticatedOrOptions
                          ,)
class MyCustomDyamicStats(FilterBasedOnRole):
    count_name = "count"
    pagination_class = MyStandardPagination
    # pagination_class = CursorSetPagination
    stats_definitions = None
    default_fields = {}

    def list(self, request, *args, **kwargs):
        self.stat_type = self.get_current_stat_type()
        if self.stat_type not in self.stats_definitions:
            raise MyCustomException("Supported types are: {}".format(",".join(self.stats_definitions)))

        queryset = self.filter_queryset(self.get_queryset())

        ## Filter based on definitions
        enabled_filters = stat_utils.get_enabled_filters(self.stats_definitions, self.stat_type)
        # print(enabled_filters)
        if enabled_filters:
            queryset = queryset.filter(**enabled_filters)

        queryset = self.get_my_queryset(queryset)
        queryset = self.get_grouped_by_data(queryset)

        paginator = self.request.query_params.get("paginator", "standard")

        # if paginator == "cursor":
        #     self.pagination_class = CursorSetPagination
        # else:
        #     self.pagination_class = MyStandardPagination

        # if self.pagination_class == CursorSetPagination:
        #     if self.stat_type == "id":
        #         setattr(self.pagination_class, "ordering", "id")
        #     else:
        #         setattr(self.pagination_class, "ordering", "value")

        self.pagination_class = MyStandardPagination

        export = True if self.request.query_params.get("export") == "true" else False
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

            xp = Export.objects.create(name="Export {}s by {}".format(self.get_model_name(), self.get_stat_type_name()), args=parsedDescriptions, user_id=self.request.user.id)

            headers = self.get_headers(queryset.first())
            filters = self.get_possible_filters()
            query_params = self.request.query_params
            export_students_reports(
                xp.id,
                user_id=self.request.user.id,
                verbose_name=xp.name,
                model_name=self.get_model_name(),
                app_name=self.get_model_app_name(),
                count_name=self.count_name,
                query_params=query_params,
                stat_type=self.stat_type,
                headers=headers,
                filters=filters,
                creator=xp,
            )
            return Response({"id": xp.id, "name": xp.name, "status": xp.get_status_display()}, status=201)

        page = self.paginate_queryset(queryset)
        ##Introduce some sort of formatting
        if page is not None:
            # serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(page)
        # serializer = self.get_serializer(queryset, many=True)
        return Response(queryset)

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
        # print(filters)
        options = {fp.field_name: {"lookup_expr": fp.lookup_expr, "value": self.request.query_params.get(key)} for key, fp in filters.items() if key in self.request.query_params}
        return options

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
                "id",
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
        }

    def get_grouped_by_data(self, queryset):
        kwargs = self.get_utils_kwargs()
        att = stat_utils.get_grouped_by_data(queryset, self.stats_definitions, kwargs)
        return stat_utils.my_order_by(att, kwargs)


class MyCustomDyamicStatsDeprecatd(object):
    count_name = "count"
    SUPPOERTED_STAT_TYES=[]

    def list(self, request, *args, **kwargs):
        self.stat_type = self.kwargs.get("type").replace("/", "")
        if self.stat_type not in self.SUPPOERTED_STAT_TYES:
            raise MyCustomException("Supported types are: {}".format(",".join(self.SUPPOERTED_STAT_TYES)))
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.get_my_queryset(queryset)
        queryset = self.get_grouped_by_data(queryset)

        ### Check if its
        if self.request.query_params.get("export", False):
            queryset_count= queryset.count()
            if self.stat_type=="id":
                queryset=self.get_serializer(queryset,many=True).data
            if queryset_count > 0:
                headers = self.get_headers(queryset[0])
                title = "{} Export".format(self.stat_type.title())
                filename = "{} {}".format(title, timezone.now().strftime("%c"))
                path = exportcsv(headers=headers, title=title, filename=filename, queryset=queryset,
                                 request=self.request)
                return Response({"path": path})

        page = self.paginate_queryset(queryset)
        ##Introduce some sort of formatting
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_headers(self, row):
        return [{"name": self.get_header_title(value), "value": value} for value in row]

    def get_header_title(self, name):
        if name == "value":
            return self.stat_type.title()

        return name.replace("_", " ").title()

    def get_comparison_fields(self):
        if self.stat_type not in self.stats_definitions or "extra_fields" not in self.stats_definitions[self.stat_type]:
            return self.get_fields()
        return {**self.get_fields(), **self.stats_definitions[self.stat_type]["extra_fields"]}

    def get_annotate_resp_fields(self):
        return ["value", *[field for field in self.get_comparison_fields()]]

    def get_group_by(self):
        if self.stat_type not in self.stats_definitions or "value" not in self.stats_definitions[self.stat_type]:
            raise MyCustomException("{} not configure properly", self.stat_type)
        return self.stats_definitions[self.stat_type]["value"]

    def my_order_by(self, queryset):
        order = self.request.query_params.get("order", None)
        order_by = self.request.query_params.get("order_by", None)
        order_by_field = self.get_order_by_default_field()
        if order_by:
            order_by_field = order_by
        if order:
            if order.lower() == "asc":
                return queryset.order_by(order_by_field)
            elif order.lower() == "desc":
                return queryset.order_by("-{}".format(order_by_field))
        return queryset.order_by(order_by_field)

    def get_order_by_default_field(self):
        return self.count_name

    def get_my_queryset(self, queryset):
        return queryset

    def get_fields(self):
        return {
            self.count_name: Count("id", distinct=True)
        }

    def get_grouped_by_data(self, queryset):
        if self.stat_type=="id":
            return self.my_order_by(queryset)

        att = queryset \
            .annotate(value=self.get_group_by()) \
            .values("value") \
            .annotate(**self.get_comparison_fields()) \
            .values(*self.get_annotate_resp_fields())
        return self.my_order_by(att)



class MyCreateModelMixin(object):
    """
    Create a model instance.
    """
    object_id=None
    def create(self, request, *args, **kwargs):
        data=request.data.copy()
        data[self.foreign_key_field]=self.get_parent_id()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_parent_id(self):
        if "pk" not in self.kwargs:
            raise MyCustomException("Id is required in the url.")
        id = self.kwargs["pk"]
        if self.foreign_key_field == None:raise MyCustomException("A foreign key field is required.")
        if self.object_id != None:return self.object_id

        ##Get the parent model
        foreignmodel = self.queryset.model._meta.get_field(self.foreign_key_field).remote_field.model
        if  not foreignmodel.objects.filter(id=id).exists() :
            raise MyCustomException(foreignmodel.__name__+" does not exist.",404)
        self.object_id=id
        return id

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class MyListModelMixin(object):
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        ##Add foreign key filtering
        queryset=queryset.filter(**{self.foreign_key_field:self.get_parent_id()})
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_parent_id(self):
        if "pk" not in self.kwargs:
            raise MyCustomException("A foreign key  is required in the url.")
        id = self.kwargs["pk"]
        if self.foreign_key_field == None: raise MyCustomException("A foreign key field is required.")
        if self.object_id != None: return self.object_id

        ##Get the parent model
        foreignmodel = self.queryset.model._meta.get_field(self.foreign_key_field).rel.to
        if not foreignmodel.objects.filter(id=id).exists():
            raise MyCustomException(foreignmodel.__name__ + " does not exist.", 404)
        self.object_id = id
        return id