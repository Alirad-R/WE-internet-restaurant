from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, ReturnRequestViewSet,
    sales_by_product, sales_by_date, best_sellers,
    worst_sellers, low_stock_alerts, sales_summary,
    product_performance
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'returns', ReturnRequestViewSet, basename='return-request')

urlpatterns = [
    path('', include(router.urls)),
    # Sales report endpoints
    path('reports/sales-by-product/', sales_by_product, name='sales-by-product'),
    path('reports/sales-by-date/', sales_by_date, name='sales-by-date'),
    path('reports/best-sellers/', best_sellers, name='best-sellers'),
    path('reports/worst-sellers/', worst_sellers, name='worst-sellers'),
    path('reports/low-stock-alerts/', low_stock_alerts, name='low-stock-alerts'),
    path('reports/sales-summary/', sales_summary, name='sales-summary'),
    path('reports/product-performance/<int:product_id>/', product_performance, name='product-performance'),
] 