from rest_framework import serializers


class InstanceSummarySerializer(serializers.Serializer):
    class Meta:
        resource_name = "instances-summary"


class ClaimSummarySerializer(serializers.Serializer):
    class Meta:
        resource_name = "claims-summary"


class ActivationSummarySerializer(serializers.Serializer):
    class Meta:
        resource_name = "activations-summary"


class InstancesCycleTimeSerializer(serializers.Serializer):
    class Meta:
        resource_name = "instances-cycle-times"
