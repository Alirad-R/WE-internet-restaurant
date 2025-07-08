from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductAlertViewSet, AlertNotificationViewSet,
    product_popularity_metrics, trending_products
)

router = DefaultRouter()
router.register(r'alerts', ProductAlertViewSet, basename='product-alert')
router.register(r'notifications', AlertNotificationViewSet, basename='alert-notification')

urlpatterns = [
    path('', include(router.urls)),
    path('metrics/popularity/', product_popularity_metrics, name='product-popularity-metrics'),
    path('metrics/trending/', trending_products, name='trending-products'),
] 