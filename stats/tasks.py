from background_task import background
from django.apps import apps
from django.db.models import F, Value, DateField, Count, Q
from django.db.models.functions import Concat, Trunc, TruncDate

from mylib.my_common import filter_queryset_based_on_role
from mylib.queryset2excel import exportExcelSheetOptimized

from core.model_definitions import models_definitions
from stats.models import Export
from stats.utils import get_grouped_by_data, my_order_by, get_formatted_filter_set



def get_model_stats_definitions(model_name):
    return models_definitions[model_name]


@background(schedule=1)
def export_students_reports(export_id, **kwargs):
    print("JOB\tExport:#{}".format(export_id))
    print(kwargs)
    # User = apps.get_model(app_label='auth', model_name='User')
    headers = kwargs.get("headers")
    model_name = kwargs.get("model_name")
    app_name = kwargs.get("app_name")

    model = apps.get_model(app_name, model_name)

    queryset = model.objects.all()

    all_definitions = get_model_stats_definitions(model_name)

    definitions = all_definitions["stats_definition"]
    kwargs["default_fields"] = all_definitions["default_fields"]

    ## Filter queryset base on role
    queryset = filter_queryset_based_on_role(queryset, kwargs.get("user_id"))

    ## Filter queryset
    filters = get_formatted_filter_set(definitions, kwargs)
    queryset = queryset.filter(**filters)

    ## Include deinitions filters

    queryset = get_grouped_by_data(queryset, definitions, kwargs)
    # Count before ordering
    rows_count = queryset.count()
    xp = Export.objects.get(id=export_id)
    xp.start(rows_count)
    queryset = my_order_by(queryset, kwargs)
    exportExcelSheetOptimized(export_id, queryset.iterator(chunk_size=3000), headers, filename=xp.name)
