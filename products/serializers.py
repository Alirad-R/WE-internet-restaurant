# products/serializers.py
from rest_framework import serializers
from .models import Product, Category

# These are placeholder serializers that will be implemented when the product models are defined

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories
    """
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for products
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Product
        fields = '__all__' 