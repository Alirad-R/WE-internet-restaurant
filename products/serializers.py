from rest_framework import serializers
from .models import Product, Category, Attribute, AttributeValue, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']

class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer()
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'value']
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
class ProductSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)
    attribute_values = AttributeValueSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'