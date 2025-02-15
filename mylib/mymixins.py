from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.utils import timezone
from mylib.my_common import MyCustomException, MyDjangoFilterBackend, MyIsAuthenticatedOrOptions
from mylib.queryset2excel import exportcsv


class MyViewMixin(object):
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (MyIsAuthenticatedOrOptions
                          ,)

class MyCustomDyamicStats(object):
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