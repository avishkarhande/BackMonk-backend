from rest_framework import serializers
from .models import Models

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Models
        fields = ('name', 'priority', 'json', 'model')