from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, AttributeViewSet, AttributeValueViewSet, TagViewSet, ProductImageViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'attributes', AttributeViewSet)
router.register(r'attribute_values', AttributeValueViewSet)
router.register(r'tags', TagViewSet)
router.register(r'product-images', ProductImageViewSet)


urlpatterns = router.urls# products/urls.py