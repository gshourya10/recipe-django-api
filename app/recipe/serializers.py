from rest_framework import serializers
from core.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags model
    """

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingredient model
    """

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']
