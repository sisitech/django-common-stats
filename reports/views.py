from rest_framework import generics

from mylib.pdf import generate_pdf
from rest_framework.response import Response
from mylib.my_common import ensure_dir_or_create

from reports.serializers import PdfReportSerializer
from django.conf import settings
from os import path
from mylib.my_common import setToJson


class TestReportPdf(generics.CreateAPIView):
    serializer_class = PdfReportSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template_name = serializer.validated_data.get("name", "")
        template = f"{template_name}.html"
        report_type = serializer.validated_data.get("type", "pdf")
        data = {}
        filaname = "Rep"
        exports_dir_name = "Pdf"
        file_path = path.join(settings.MEDIA_ROOT, exports_dir_name, "{}.{}".format(filaname, report_type))
        ensure_dir_or_create(path.join(settings.MEDIA_ROOT, exports_dir_name))
        generate_pdf(template, data, file_path, report_type)
        return Response({"file_path": file_path})
