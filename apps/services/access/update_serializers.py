from rest_framework import serializers


class EditableSubmissionUpdateSerializer(
    serializers.Serializer
):

    data = serializers.JSONField()