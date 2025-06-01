from rest_framework import serializers


class ServiceAuthCodeSerializer(serializers.Serializer):
    authorization_code = serializers.CharField()
