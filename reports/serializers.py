from rest_framework import serializers

from reports.data_pipeline import get_any_stats


REPORT_TYPES = (
    ("pdf", "PDF"),
    ("png", "PNG"),
    ("html", "HTML"),
)


class PdfReportSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=REPORT_TYPES, default="pdf")


from django.utils import timezone
from stats.models import Export


class CustomReportStatisticField(serializers.Field):
    data_key = ""
    grouping = ""

    def __init__(self, data_key="", grouping=None, **kwargs):
        kwargs["read_only"] = True
        self.data_key = data_key
        self.grouping = grouping
        kwargs["source"] = "user"
        super(CustomReportStatisticField, self).__init__(**kwargs)

    def to_representation(self, value):
        query_params = self.context.get("query_params", {})
        # parent_instance = self.parent.instance
        return get_any_stats(self.data_key, user=value, grouping=self.grouping, query_params=query_params)


class CustomReportBaseSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(default="Sample Title")
    subtitle = serializers.ReadOnlyField(default="Sample Subtlte")
    generated_on = serializers.ReadOnlyField(default=timezone.now())
    start_date = serializers.ReadOnlyField(required=False)
    end_date = serializers.ReadOnlyField(required=False)

    cache_data = {}

    class Meta:
        model = Export
        fields = "__all__"
