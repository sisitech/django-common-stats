from django.conf.urls import url

from reports.views import TestReportPdf


urlpatterns = [
    url(r"^$", TestReportPdf.as_view(), name="test_pdf_export"),
]
