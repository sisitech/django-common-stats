from rest_framework import serializers


REPORTS = (
    ("main", "main_report.html"),
    ("main", "main_report.html"),
)

REPORT_TYPES = (
    ("pdf", "PDF"),
    ("png", "PNG"),
    ("html", "HTML"),
)


class PdfReportSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=REPORT_TYPES, default="pdf")
