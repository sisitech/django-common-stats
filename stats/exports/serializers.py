
from rest_framework import serializers
from stats.models import Export
from stats.serializers import MyCustomSerializerField


class ExportSerializer(serializers.ModelSerializer):
    status_display=serializers.CharField(source="get_status_display",read_only=True)
    completed_percentage=serializers.ReadOnlyField()
    rows_count=MyCustomSerializerField()
    exported_rows_count=MyCustomSerializerField()
    duration=serializers.ReadOnlyField()
    class Meta:
        model=Export
        fields=("__all__")
