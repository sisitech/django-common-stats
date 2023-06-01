import traceback
from background_task import background

from django.apps import apps
from core.custom_reports import CUSTOM_REPORTS

from mylib.my_common import ensure_dir_or_create
from mylib.pdf import generate_pdf
from django.conf import settings
from os import path
from django.core.files.storage import default_storage
import os
import sys


@background(schedule=1)
def export_custom_reports(export_id, **kwargs):
    Export = apps.get_model("stats", "Export")
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
        print(res)
        if "test" in sys.argv:
            try:
                new_path = os.path.join(settings.MEDIA_ROOT, res)
                print(new_path)
            except Exception as e:
                pass
        export.finish(res)
        try:
            os.remove(file_path)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        end_error(str(e))
