from rest_framework import serializers
from .models import Product, Category, Attribute, AttributeValue, Tag, ProductImage

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

class NestedProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    attribute_values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'tags', 'attribute_values', 'images']

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    products = NestedProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'products']

    # def get_products(self, obj):
    #     return [{'id': product.id, 'name': product.name} for product in obj.products.all()]
        # from .serializers import ProductSerializer  # delayed import
        # return ProductSerializer(obj.products.all(), many=True).data

        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

        
class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True)
    
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = AttributeValueSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_id', 'image', 'tags', 'tag_ids', 'attribute_values', 'images', 'is_available', 'is_featured']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate(self, data):
        # Custom cross-field validation
        if data.get('is_featured') and not data.get('is_available'):
            raise serializers.ValidationError("Featured products must be available")
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tag_ids', [])
        product = Product.objects.create(**validated_data)
        product.tags.set(tags)
        return product

    def update(self, instance, validated_data):
        tags = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance

        
    