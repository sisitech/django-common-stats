import collections
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
    response_type = None
    value = None

    def __init__(self, data_key="", annotates=[], grouping=None, response_type=None, value=None, value_field=None, **kwargs):
        kwargs["read_only"] = True
        self.data_key = data_key
        self.grouping = grouping
        self.value = value
        self.value_field = value_field
        self.annotates = annotates
        self.response_type = response_type
        kwargs["source"] = "user"
        super(CustomReportStatisticField, self).__init__(**kwargs)

    def to_representation(self, value):
        query_params = self.context.get("query_params", {})
        # parent_instance = self.parent.instance
        kwargs = {
            "value": self.value,
            "value_field": self.value_field,
            "annotates": self.annotates,
        }

        formatted_data = get_any_stats(self.data_key, user=value, grouping=self.grouping, response_type=self.response_type, query_params=query_params, **kwargs)
        response_data_type = type(formatted_data)
        if response_data_type == list or response_data_type == collections.OrderedDict:
            annotates = kwargs.get("annotates", [])
            for annotate in annotates:
                # Example {"data_key": "students", "grouping": "id", "name": "students"}
                print(annotate)

        return formatted_data


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
