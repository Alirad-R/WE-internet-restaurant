from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing product instances.
    """
    queryset = Product.objects.all()  # Fixed empty queryset
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Return a list of featured products
        """
        featured = Product.objects.filter(is_featured=True, is_available=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing category instances.
    """
    queryset = Category.objects.all()  # Fixed empty queryset
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
