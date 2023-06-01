from rest_framework import serializers


REPORT_TYPES = (
    ("pdf", "PDF"),
    ("png", "PNG"),
    ("html", "HTML"),
)


class PdfReportSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=REPORT_TYPES, default="pdf")
