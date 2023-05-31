import os
from background_task import background
from django.apps import apps
from django.db.models import F, Value, DateField, Count, Q
from django.db.models.functions import Concat, Trunc, TruncDate

from mylib.my_common import filter_queryset_based_on_role
from mylib.my_common import ensure_dir_or_create
from django.core.files.storage import default_storage

from core.custom_reports import CUSTOM_REPORTS
from mylib.pdf import generate_pdf
from mylib.queryset2excel import exportExcelSheetOptimized
from reports.utils import BaseCustomReport

from stats.models import Export
from stats.utils import get_grouped_by_data, my_order_by, get_formatted_filter_set, get_model_stats_definitions
from django.conf import settings
from os import path


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


@background(schedule=1)
def export_custom_reports(export_id, **kwargs):
    query = Export.objects.filter(id=export_id, is_custom=True)

    def start_export():
        print("Hello the start")
        query.update(
            **{
                "rows_count": 0,
                "exported_rows_count": 0,
                "status": "E",
                "errors": "",
            }
        )

    def end_error(error):
        query.update(
            **{
                "status": "F",
                "errors": error,
            }
        )

    def prepare_download():
        query.update(
            **{
                "status": "P",
            }
        )

    if not query.exists():
        return
    export = query.first()
    name = export.name
    if name not in CUSTOM_REPORTS:
        export.errors = f"{name} Not implemented in core.custom_reports.CUSTOM_REPORTS"
        return
    report = CUSTOM_REPORTS[name]
    template = report.template
    # print(template)
    filaname = "Rep"

    try:
        start_export()
        args = report.get_context(export)
        prepare_download()
        filaname = f"{name}-{export.title}-{export.id}".replace(" ", "_").lower()
        exports_dir_name = "CustomExports"
        export_type = "csv" if export.type == "C" else "pdf"

        # file_path = path.join(settings.MEDIA_ROOT, exports_dir_name, "{}.{}".format(filaname, export_type))
        file_path = "{}.{}".format(filaname, export_type)

        # ensure_dir_or_create(path.join(settings.MEDIA_ROOT, exports_dir_name))
        # print(template)

        generate_pdf(template, args, file_path, export_type)
        export = query.first()
        # print(file_path)
        final_file_path = path.join(exports_dir_name, "{}.{}".format(filaname, export_type))

        res = default_storage.save(final_file_path, open(file_path, "rb"))
        export.finish(res)
        try:
            os.remove(file_path)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
        end_error(str(e))
