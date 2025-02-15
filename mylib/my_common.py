import enum
import os
import sys
from unittest import skip
import django_filters
from background_task import background
from django.core.mail import send_mail
from functools import reduce
from operator import or_
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from django.db.models import Case, When, Value
from datetime import timedelta
from django.utils import timezone
from oauthlib import common
from oauth2_provider.settings import oauth2_settings


from django.conf import settings
from django.db import models
from django.db.models import Q, CharField

from oauth2_provider.models import AccessToken, RefreshToken, Application

def skip_if(condition, reason):
    def decorator(test_method):
        if condition:
            return skip(reason)(test_method)
        return test_method

    return decorator

def generateUserToken(activated_user):
    default_client_id = "kadkmalkm218n21b9721u2ji12"
    default_client_secret = "ueiuuew893iueiwyeiuwyiu"
    application = Application.objects.get_or_create(client_id=default_client_id, name="autoLogin", authorization_grant_type="password", client_type="public", client_secret=default_client_secret)
    application = application[0]
    expires = timezone.now() + timedelta(seconds=60 * 60 * 12 * 365)
    access_token = AccessToken(user=activated_user, scope="", expires=expires, token=common.generate_token(), application=application)
    access_token.save()
    refresh_token = RefreshToken(user=activated_user, token=common.generate_token(), application=application, access_token=access_token)
    refresh_token.save()
    return {"access_token": access_token.token, "refresh_token": refresh_token.token, "token_type": "Bearer", "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS}

class MyItemsViewMixin(object):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset

        return self.queryset.filter(user_id=self.request.user.id)


class MyUserRoles(enum.Enum):
    A = "Admin"
    SCHA = "School Admin"
    SCHT = "School Teacher"
    SHYA = "Shahiya Admin"
    DSTA = "District Admin"
    RGNA = "Region Admin"


"""
from mylib.my_common import get_redirect_url

mylib.my_common.MyStandardPagination
get_redirect_url()
"""
from datetime import date

from drf_autodocs.views import TreeView
from django.contrib.auth import get_user_model

# from django.contrib.auth.mixins import LoginRequiredMixin

# MyUser = get_user_model()
def is_in_test_mode():
    is_testing = "test" in sys.argv
    if is_testing:
        print("Running now in test mode")
    return is_testing


def calculate_age_in_days(birth_date):
    today = date.today()
    age = (today - birth_date).days
    return age


def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year

    # Check if the birthday has occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1

    return age


def setToJson(SET_OBJ):
    return {c[0]: c[1] for c in SET_OBJ}


FORM_STAGES = (
    ("R", "Reception"),
    ("T", "Triage"),
    ("C", "Cashier"),
    ("D", "Doctor"),
    ("CL", "Cashier Lab"),
    ("L", "Lab"),
    ("DFL", "Doctor From Lab"),
    ("CP", "Cashier Pharmacy"),
    ("P", "Pharmacy"),
)


class MyCustomException(APIException):
    status_code = 503
    detail = "Service temporarily unavailable, try again later."
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"

    def __init__(self, message, code=400):
        self.status_code = code
        self.default_detail = message
        self.detail = message


class RequirableBooleanField(serializers.BooleanField):
    default_empty_html = serializers.empty


class MyModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("id",)


def is_test_mode():
    return "test" in sys.argv

def case_generator(options_set: set, field_name: str, default="", override_values={}, output_field=CharField()):
    original_options_map = dict((x, Value(y)) for x, y in options_set)
    options_map = {**original_options_map, **override_values}
    # print(options_map)
    return Case(*[When(**{field_name: option, "then": options_map[option]}) for option in options_map], output_field=output_field)


def get_digitalocean_spaces_download_url(filepath):
    return ""


def ensure_dir_or_create(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


class MyStandardPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = "page_size"


class ProtectedURlsView(TreeView):
    pass


class MyDjangoFilterBackend(DjangoFilterBackend):
    myfilter_class = None

    def get_filterset_class(self, view, queryset=None):
        return self.get_filter_class(view=view,querysetPassed=queryset)

    def get_filter_class(self, view, querysetPassed=None):
        """
        Return the django-filters `FilterSet` used to filter the queryset.
        """
        if self.myfilter_class:
            return self.myfilter_class

        queryset = getattr(view, "queryset", None)
        extra_fields = getattr(view, "extra_filter_fields", None)
        filter_mixin = getattr(view, "filter_mixin", None)

        try:
            # print("Tryine")
            # print(queryset, view)
            model = queryset.model
            filter_model = model
            ##print"The filter class ...")
            filter_class = self.get_dynamic_filter_class(model, extra_fields=extra_fields, filter_mixin=filter_mixin)
            ##print"The filter class ...")
            assert issubclass(queryset.model, filter_model), "FilterSet model %s does not match queryset model %s" % (
                filter_model,
                queryset.model,
            )
            self.myfilter_class = filter_class
            return filter_class
        except Exception as e:
            print(e)
            raise MyCustomException("Dynamic Filter class error.")

    def get_dynamic_filter_class(self, model_class, extra_fields=None, filter_mixin=None):
        excluded_fields = ("none",)

        if hasattr(settings, "MYDJANGOFILTERBACKEND_EXCLUDED_FILTER_FIELDS"):
            excluded_fields = settings.MYDJANGOFILTERBACKEND_EXCLUDED_FILTER_FIELDS

        # print("Exclueds are",excluded_fields)
        class Meta:
            model = model_class
            exclude = (
                "file",
                "plate_number_image",
                "errors_file",
                "import_file",
                "moe_extra_info",
                "before_image",
                "after_image",
                "image",
                "recording",
                "logo",
                "avatar",
                "location",
                "translations",
            ) + excluded_fields  # [f.name for f in model_class.fields if  f.name in ["logo","image","file"]]
            fields = "__all__"
            filter_overrides = {
                models.CharField: {
                    "filter_class": django_filters.CharFilter,
                    "extra": lambda f: {
                        "lookup_expr": "icontains",
                    },
                }
            }

        attrs = {
            "Meta": Meta,
        }

        ##Append the extraFields
        if extra_fields:
            for field in extra_fields:
                extra_field = self.get_etxra_fields(**field)
                filter_name = f"{field['label']}".replace(" ", "_").lower().strip()
                if extra_field:
                    attrs[filter_name] = extra_field

        if filter_mixin:
            filter_class = type(
                model_class.__class__.__name__ + "FilterClass",
                (filter_mixin, FilterSet),
                attrs,
            )
        else:
            filter_class = type(model_class.__class__.__name__ + "FilterClass", (FilterSet,), attrs)
        return filter_class

    def get_etxra_fields(self, field_name, label, field_type, lookup_expr="exact"):
        if field_type == "number":
            return django_filters.NumberFilter(field_name=field_name, label=label, lookup_expr=lookup_expr)
        elif field_type == "char":
            return django_filters.CharFilter(field_name=field_name, label=label, lookup_expr="icontains")
        elif field_type == "bool":
            return django_filters.BooleanFilter(field_name=field_name, label=label, lookup_expr=lookup_expr)
        elif field_type == "date":
            return django_filters.DateFilter(field_name=field_name, label=label, lookup_expr=lookup_expr)
        elif field_type == "datetime":
            return django_filters.DateTimeFilter(field_name=field_name, label=label, lookup_expr=lookup_expr)
        else:
            return None


# class MyDjangoFilterBackend(DjangoFilterBackend):
#     myfilter_class = None
#
#     def get_filter_class(self, view, queryset=None):
#         """
#         Return the django-filters `FilterSet` used to filter the queryset.
#         """
#         if self.myfilter_class:
#             return self.myfilter_class
#         extra_fields=getattr(view,'extra_filter_fields',None)
#
#         try:
#             model = queryset.model
#             filter_model = model
#             ##print"The filter class ...")
#             filter_class = self.get_dynamic_filter_class(model,extra_fields=extra_fields)
#             ##print"The filter class ...")
#             assert issubclass(queryset.model, filter_model), \
#                 'FilterSet model %s does not match queryset model %s' % \
#                 (filter_model, queryset.model)
#             self.myfilter_class = filter_class
#             return filter_class
#         except Exception as e:
#             print(e)
#             raise MyCustomException("Dynamic Filter class error.")
#
#     def get_dynamic_filter_class(self, model_class,extra_fields=None):
#         class Meta:
#             model = model_class
#             exclude = ('file', 'image','recording','moe_extra_info')  # [f.name for f in model_class.fields if  f.name in ["logo","image","file"]]
#             fields = ("__all__")
#             filter_overrides = {
#                 models.CharField: {
#                     'filter_class': django_filters.CharFilter,
#                     'extra': lambda f: {
#                         'lookup_expr': 'icontains',
#                     },
#                 }
#             }
#
#         attrs = {"Meta": Meta,}
#
#         ##Append the extraFields
#         if extra_fields:
#             for field in extra_fields:
#                 extra_field=self.get_etxra_fields(**field)
#                 if extra_field:attrs[field["field_name"]]=extra_field
#
#         filter_class = type(model_class.__class__.__name__ + "FilterClass", (FilterSet,), attrs)
#         return filter_class
#
#     def get_etxra_fields(self,field_name,label,field_type,lookup_expr="exact"):
#         if field_type=="number" :
#             return django_filters.NumberFilter(field_name=field_name,label=label,lookup_expr=lookup_expr)
#         elif field_type=="char":
#             return django_filters.CharFilter(field_name=field_name,label=label,lookup_expr="icontains")
#         elif field_type=="date":
#             return django_filters.DateFilter(field_name=field_name,label=label,lookup_expr=lookup_expr)
#         elif field_type=="datetime":
#             return django_filters.DateTimeFilter(field_name=field_name,label=label,lookup_expr=lookup_expr)
#         else:
#             return None


"""
from mylib.my_common import MySendEmail as se

data={"verify_url":"Micha","name":"mwangi Micha","old_password":"hello"}
se("Test email","new_user.html",data,["michameiu@gmail.com"])

"""


@background(schedule=1,queue="send-email")
def MySendEmail(subject, template, data, recipients, from_email=None):
    print("JOB EMAIL :  {}".format(template))
    if from_email == None:
        from_email = settings.DEFAULT_FROM_EMAIL
    rendered = render_to_string(template, data)
    # print("Sending email...")

    if settings.DISABLE_EMAIL_SENDING:
        print("Sending emails disabled")
        return
    try:
        print(from_email, recipients)
        ema = send_mail(
            subject=subject,
            message="",
            html_message=rendered,
            from_email=from_email,
            recipient_list=recipients,  # ['micha@sisitech.com'],
            fail_silently=False,
            # reply_to="room@katanawebworld.com"
        )
        return ema
    except Exception as e:
        print(e)
        print("Failed to send email")
        return None


def tuple_choices_to_map(tupleChoices):
    choices = {}
    for choice in tupleChoices:
        if len(choice) == 2:
            value = choice[0]
            variant = choice[1].lower()
            choices[variant] = value
            choices[value.lower()] = value
    return choices


class MyStandardPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = "page_size"


class MyIsAuthenticatedOrOptions(BasePermission):
    safe_methods = [
        "OPTIONS",
    ]

    def has_permission(self, request, view):
        if request.method in self.safe_methods:
            return True
        return request.user.is_authenticated


def str2bool(value):
    trues = ["yes", "true", "1"]
    if value and value.lower() in trues:
        return True
    return False


def get_get_next_stage(previous_stage):
    stages = [d[0] for d in FORM_STAGES]
    index = stages.index(previous_stage)
    next_index = index + 1 if index < len(stages) else index
    # print("{} ==> {}".format(previous_stage, next_index))
    return stages[next_index]


# def get_filters_as_array(filter_args):
#     filter_values = map(lambda x: x.strip(), filter_args.split(","))
#     return list(filter_values)


# def filter_queryset_based_on_role(queryset, user_id=None):
#     model = queryset.model
#     if user_id == None:
#         return queryset

#     if not hasattr(model, "get_role_filters"):
#         return queryset
#     filters = model.get_role_filters()

#     user = get_user_model().objects.get(id=user_id)

#     role = user.role
#     filter_args = user.filter_args
#     filter_param = filters.get(role, None)
#     if role == "A" or filter_args == None or filter_param == None:
#         # print("hello")
#         return queryset

#     # check if its an array
#     filter_values = get_filters_as_array(filter_args)
#     # print(filter_values)

#     filter_param_in = f"{filter_param}__in"
#     filters = {filter_param_in: filter_values}
#     print(filters)
#     return queryset.filter(**filters)


# class FilterBasedOnRole(object):
#     def get_queryset(self):
#         assert self.queryset is not None, "'%s' should either include a `queryset` attribute, " "or override the `get_queryset()` method." % self.__class__.__name__

#         queryset = self.queryset
#         if isinstance(queryset, QuerySet):
#             # Ensure queryset is re-evaluated on each request.
#             queryset = queryset.all()
#         return self.filter_queryset_on_role(queryset)

#     def filter_queryset_on_role(self, queryset):
#         return filter_queryset_based_on_role(queryset, user_id=self.request.user.id)


def get_filters_as_array(filter_args):
    filter_values = map(lambda x: x.strip(), filter_args.split(","))
    return list(filter_values)


def filter_queryset_based_on_role(queryset, user_id=None):
    model = queryset.model

    if user_id == None:
        return queryset

    if not hasattr(model, "get_role_filters"):
        return queryset

    filters = model.get_role_filters()

    user = get_user_model().objects.get(id=user_id)

    role = user.role
    filter_args = user.filter_args
    filter_param = filters.get(role, None)
    # print("Gerre")
    # print(role, filter_args, filter_param)

    if role == "A" or filter_args == None or filter_param == None:
        return queryset

    print(type(filter_param) == str)

    filter_values = get_filters_as_array(filter_args)

    if type(filter_param) == list:
        qs = []
        for index, filter_p in enumerate(filter_param):
            filter_param_in = f"{filter_p}__in"
            fields = {filter_param_in: filter_values}
            qs.append(Q(**fields))
            filters = {filter_param[index]: filter_args}

        query = reduce(or_, qs)
        # print(query)
        return queryset.filter(query)

    # print(filter_values)

    filter_param_in = f"{filter_param}__in"
    filters = {filter_param_in: filter_values}
    # print(filters)
    return queryset.filter(**filters)


class FilterBasedOnRole(object):
    def get_queryset(self):
        assert self.queryset is not None, "'%s' should either include a `queryset` attribute, " "or override the `get_queryset()` method." % self.__class__.__name__

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return self.filter_queryset_on_role(queryset)

    def filter_queryset_on_role(self, queryset):
        return filter_queryset_based_on_role(queryset, user_id=self.request.user.id)
