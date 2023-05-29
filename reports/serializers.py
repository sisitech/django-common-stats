from rest_framework import serializers


REPORTS = (
    ("main", "main_report.html"),
    ("main", "main_report.html"),
)

REPORT_TYPES = (
    ("pdf", "PDF"),
    ("html", "HTML"),
)


class PdfReportSerializer(serializers.Serializer):
    name = serializers.ChoiceField(choices=REPORTS)
    type = serializers.ChoiceField(choices=REPORT_TYPES, default="pdf")
