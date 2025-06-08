from django.db.models import (
    Sum, Count, Avg, F, ExpressionWrapper,
    DecimalField, FloatField, Q, Window
)
from django.db.models.functions import (
    TruncDate, TruncMonth, TruncYear,
    ExtractYear, ExtractMonth, Coalesce
)
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from products.models import Product

class SalesReportGenerator:
    """
    Class for generating various sales reports and analytics
    """
    
    @staticmethod
    def get_date_range_filters(start_date=None, end_date=None):
        """
        Get date range filters for orders
        """
        filters = Q(order__status='delivered')  # Only count delivered orders
        if start_date:
            filters &= Q(order__created_at__gte=start_date)
        if end_date:
            filters &= Q(order__created_at__lte=end_date)
        return filters

    @classmethod
    def get_sales_by_product(cls, start_date=None, end_date=None):
        """
        Get sales aggregated by product
        """
        filters = cls.get_date_range_filters(start_date, end_date)
        
        return OrderItem.objects.filter(filters).values(
            'product__id',
            'product__name',
            'product__price',
            'product__stock'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField()
                )
            ),
            order_count=Count('order', distinct=True),
            avg_order_value=ExpressionWrapper(
                F('total_revenue') / F('order_count'),
                output_field=DecimalField()
            )
        ).order_by('-total_revenue')

    @classmethod
    def get_sales_by_date(cls, group_by='day', start_date=None, end_date=None):
        """
        Get sales aggregated by date
        group_by can be 'day', 'month', or 'year'
        """
        filters = cls.get_date_range_filters(start_date, end_date)
        
        date_func = {
            'day': TruncDate('order__created_at'),
            'month': TruncMonth('order__created_at'),
            'year': TruncYear('order__created_at')
        }[group_by]

        return OrderItem.objects.filter(filters).annotate(
            date=date_func
        ).values('date').annotate(
            total_sales=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField()
                )
            ),
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity')
        ).order_by('date')

    @classmethod
    def get_best_sellers(cls, limit=10, start_date=None, end_date=None):
        """
        Get best-selling products by quantity
        """
        filters = cls.get_date_range_filters(start_date, end_date)
        
        return OrderItem.objects.filter(filters).values(
            'product__id',
            'product__name',
            'product__price',
            'product__stock'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField()
                )
            )
        ).order_by('-total_quantity')[:limit]

    @classmethod
    def get_worst_sellers(cls, limit=10, start_date=None, end_date=None):
        """
        Get worst-selling products by quantity
        """
        filters = cls.get_date_range_filters(start_date, end_date)
        
        return OrderItem.objects.filter(filters).values(
            'product__id',
            'product__name',
            'product__price',
            'product__stock'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField()
                )
            )
        ).order_by('total_quantity')[:limit]

    @classmethod
    def get_low_stock_alerts(cls, threshold=10):
        """
        Get products with stock below threshold
        """
        return Product.objects.filter(
            stock__lte=threshold,
            is_active=True
        ).annotate(
            total_pending_orders=Coalesce(
                Sum(
                    'orderitem__quantity',
                    filter=Q(orderitem__order__status__in=['pending', 'processing'])
                ),
                0
            )
        ).values(
            'id',
            'name',
            'stock',
            'total_pending_orders'
        )

    @classmethod
    def get_sales_summary(cls, start_date=None, end_date=None):
        """
        Get overall sales summary
        """
        filters = cls.get_date_range_filters(start_date, end_date)
        
        summary = OrderItem.objects.filter(filters).aggregate(
            total_revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField()
                )
            ),
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity'),
            avg_order_value=ExpressionWrapper(
                Sum(F('quantity') * F('unit_price')) / Count('order', distinct=True),
                output_field=DecimalField()
            )
        )
        
        # Add year-over-year growth if dates provided
        if start_date and end_date:
            period_length = end_date - start_date
            previous_start = start_date - period_length
            previous_end = start_date
            
            previous_filters = cls.get_date_range_filters(previous_start, previous_end)
            previous_revenue = OrderItem.objects.filter(previous_filters).aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F('quantity') * F('unit_price'),
                        output_field=DecimalField()
                    )
                )
            )['total'] or 0
            
            current_revenue = summary['total_revenue'] or 0
            if previous_revenue > 0:
                summary['growth_rate'] = ((current_revenue - previous_revenue) / previous_revenue) * 100
            else:
                summary['growth_rate'] = 100 if current_revenue > 0 else 0
        
        return summary

    @classmethod
    def get_product_performance_metrics(cls, product_id, start_date=None, end_date=None):
        """
        Get detailed performance metrics for a specific product
        """
        filters = cls.get_date_range_filters(start_date, end_date)
        filters &= Q(product_id=product_id)
        
        return OrderItem.objects.filter(filters).aggregate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('quantity') * F('unit_price'),
                    output_field=DecimalField()
                )
            ),
            order_count=Count('order', distinct=True),
            avg_order_value=ExpressionWrapper(
                Sum(F('quantity') * F('unit_price')) / Count('order', distinct=True),
                output_field=DecimalField()
            ),
            avg_quantity_per_order=ExpressionWrapper(
                Cast(Sum('quantity'), FloatField()) / Cast(Count('order', distinct=True), FloatField()),
                output_field=FloatField()
            )
        ) 