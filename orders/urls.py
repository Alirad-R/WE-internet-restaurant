from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, CartViewSet, WalletViewSet, ReturnRequestViewSet,
    sales_by_product, sales_by_date, best_sellers,
    worst_sellers, low_stock_alerts, sales_summary,
    product_performance, admin_transactions, test_sales_summary, test_admin_transactions, create_test_order
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'wallet', WalletViewSet, basename='wallet')
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
    # Admin endpoints
    path('admin/transactions/', admin_transactions, name='admin-transactions'),
    # Test endpoints (no authentication)
    path('test/sales-summary/', test_sales_summary, name='test-sales-summary'),
    path('test/admin/transactions/', test_admin_transactions, name='test-admin-transactions'),
    path('test/create-order/', create_test_order, name='create-test-order'),
] 