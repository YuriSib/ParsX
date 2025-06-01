from rest_framework import serializers
from .models import Integrations, Categories, Products


class IntegrationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integrations
        fields = '__all__'