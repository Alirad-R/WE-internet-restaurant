from django.contrib import admin
from .models import Product, Category, ProductImage

# @admin.register(Category) #TODO See what this code does
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'is_active', 'created_at')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'description')

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'category', 'is_available', 'is_featured')
#     list_filter = ('is_available', 'is_featured', 'category')
#     search_fields = ('name', 'description')
#     list_editable = ('is_available', 'is_featured')

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductImage)