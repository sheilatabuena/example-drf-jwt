""" This module contains serializers for messages """
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """ Serializer class for Message """

    class Meta:
        model = Message
        fields = Message.get_field_names()

    def create(self, validated_data):
        """
        Create and return a new instance, given the validated data.
        """
        instance = Message.objects.create(**validated_data)
        return instance
