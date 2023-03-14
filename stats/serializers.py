from rest_framework import serializers


class MyCustomSerializerField(serializers.Field):
    def to_representation(self, value):
        if value:
            return  ("{:,.0f}".format(value))
        return "0"

class MyCustomSerializerCurrencyField(serializers.Field):
    def to_representation(self, value):
        if value !=None:
            return  ("Ksh {:,.0f}".format(value))
        return "Ksh 0"

# class GeneralRepairStatsSerializer(serializers.Serializer):
#     total_requests=MyCustomSerializerField(read_only=True)
#     total_clients=MyCustomSerializerField(read_only=True)
#     total_sales=MyCustomSerializerCurrencyField(read_only=True,)
#     total_completed=MyCustomSerializerField(read_only=True)


class BaseDynamicStatsSerializer(serializers.Serializer):
    males=serializers.ReadOnlyField()
    females=serializers.ReadOnlyField()
    total_students=serializers.ReadOnlyField()
    value=serializers.ReadOnlyField()


class ClassStatsSerializer(BaseDynamicStatsSerializer):
    class_name=serializers.ReadOnlyField()
