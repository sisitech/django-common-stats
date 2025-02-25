from rest_framework.generics import GenericAPIView

from mylib.mymixins import MyCreateModelMixin, MyListModelMixin

from django.db.models.aggregates import Aggregate
from mylib.image import scramble, Base64ImageField
from django.conf import settings
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFit, ResizeToFill
from django.db import models
from rest_framework import generics,serializers

MyUser = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class MyImageCacheSerializer(serializers.Serializer):
    image = Base64ImageField(required=False, max_length=None, use_url=True)
    cache_image = serializers.SerializerMethodField(read_only=True)
    avatar_image = serializers.SerializerMethodField(read_only=True)

    def get_cache_image(self, obj):
        self.request = self.context.get("request")
        return get_cache_image_url(self.request, obj.image, obj.cache_image)

    def get_avatar_image(self, obj):
        self.request = self.context.get("request")
        return get_cache_image_url(self.request, obj.image, obj.avatar_image)


class RequirableBooleanField(serializers.BooleanField):
    default_empty_html = serializers.empty


def get_cache_image_url(request, image, cache_image):
    if image is None or image == "":
        return None
    if request is not None:
        return request.build_absolute_uri(cache_image.url)
    return "{}{}".format(settings.MY_SITE_URL, cache_image.url)


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
    created_by = models.ForeignKey(MyUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_%(class)ss", related_query_name="created_%(class)s", editable=False)
    updated_by = models.ForeignKey(MyUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="updated_%(class)ss", related_query_name="updated_%(class)s", editable=False)


    class Meta:
        abstract = True
        ordering = ("id",)

    @staticmethod
    def get_role_filters():
        return {}


class MyImageModel(MyModel):
    image = models.ImageField("uploads", upload_to=scramble, null=True, blank=True)
    avatar_image = ImageSpecField(source="image", processors=[ResizeToFill(360, 200)], format="JPEG", options={"quality": 80})
    cache_image = ImageSpecField(source="image", processors=[ResizeToFit(height=600)], format="JPEG", options={"quality": 30})

    class Meta:
        abstract = True
        ordering = ("id",)


class MyImageCacheSerializer(serializers.Serializer):
    image = Base64ImageField(required=False, max_length=None, use_url=True)
    cache_image = serializers.SerializerMethodField(read_only=True)
    avatar_image = serializers.SerializerMethodField(read_only=True)

    def get_cache_image(self, obj):
        self.request = self.context.get("request")
        return get_cache_image_url(self.request, obj.image, obj.cache_image)

    def get_avatar_image(self, obj):
        self.request = self.context.get("request")
        return get_cache_image_url(self.request, obj.image, obj.avatar_image)


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
