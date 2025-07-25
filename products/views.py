from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Category, Attribute, AttributeValue, Tag, ProductImage
from .serializers import ProductSerializer, CategorySerializer, AttributeSerializer, AttributeValueSerializer, TagSerializer, ProductImageSerializer
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing product instances.
    """
    queryset = Product.objects.all()  # Fixed empty queryset
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name', 'category', 'tags', 'price']
    # filterset_fields = {
    #     'price': ['gte', 'lte'],
    #     'category': ['exact'],
    #     'tags': ['exact'],
    # }
    # search_fields = ['name', 'description']
    # ordering_fields = ['price', 'created_at']
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Return a list of featured products
        """
        featured = Product.objects.filter(is_featured=True, is_available=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = []
    
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.AllowAny]

    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.AllowAny]
    
class AttributeValueViewSet(viewsets.ModelViewSet):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.AllowAny]
    
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]