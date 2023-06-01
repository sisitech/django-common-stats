from rest_framework import serializers
from mylib.my_common import setToJson, tuple_choices_to_map
from stats.models import Export
from stats.serializers import MyCustomSerializerField
from django.conf import settings

# from core.custom_reports import CUSTOM_REPORTS


# REPORT_CHOICES = ((key, key.title()) for key in CUSTOM_REPORTS)


class ExportSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    completed_percentage = serializers.ReadOnlyField()
    rows_count = MyCustomSerializerField()
    exported_rows_count = MyCustomSerializerField()
    duration = serializers.ReadOnlyField()

    class Meta:
        model = Export
        fields = "__all__"


class CustomExportSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    completed_percentage = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()

    def __init__(self, *args, **kwargs):
        super(CustomExportSerializer, self).__init__(**kwargs)
        if hasattr(settings, "CUSTOM_REPORTS"):
            # print(settings.CUSTOM_REPORTS)
            choices = list(setToJson(settings.CUSTOM_REPORTS).keys())
            # print(choices)
            choice = ""
            if len(choices) > 0:
                choice = choices[0]
            self.fields.update({"custom_report_name": serializers.ChoiceField(choices=settings.CUSTOM_REPORTS, default=choice)})

    class Meta:
        model = Export
        fields = "__all__"
