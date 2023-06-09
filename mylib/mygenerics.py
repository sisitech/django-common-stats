from rest_framework.generics import GenericAPIView

from mylib.mymixins import MyCreateModelMixin, MyListModelMixin

from django.db.models.aggregates import Aggregate

from django.db import models


class GroupConcat(Aggregate):
    function = "GROUP_CONCAT"
    template = "%(function)s(%(distinct)s %(expressions)s)"
    allow_distinct = True

    def __init__(self, expression, delimiter=None, **extra):
        if delimiter is not None:
            self.allow_distinct = False
            delimiter_expr = models.Value(str(delimiter))
            super().__init__(expression, delimiter_expr, **extra)
        else:
            super().__init__(expression, **extra)

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            function=self.function,
            template=self.template,
            **extra_context,
        )

    def as_postgresql(self, compiler, connection, **extra_context):
        # CAST would be valid too, but the :: shortcut syntax is more readable.
        function = "STRING_AGG"
        template = "%(function)s(%(distinct)s%(expressions)s)"
        return super().as_sql(
            compiler,
            connection,
            function=function,
            template=template,
            **extra_context,
        )


class MyModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("id",)

    @staticmethod
    def get_role_filters():
        return {}


class MyListCreateAPIView(MyCreateModelMixin, MyListModelMixin, GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MyListAPIView(MyCreateModelMixin, MyListModelMixin, GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
