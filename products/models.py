from django.db import models
from django.conf import settings

class Category(models.Model):
    """
    Product category model
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        
class Tag(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Product model
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    # image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    def __str__(self):
        return self.name

# class Category(models.Model):
#     name = models.CharField(max_length=200)
#     image = models.ImageField(upload_to='categories/images', blank=True, null=True)
    
#     def __str__(self):
#         return self.name
    
# class Product(models.Model):
#     name = models.CharField(max_length=200)
#     price = models.IntegerField()
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='products/images', blank=True, null=True)
#     stock = models.BooleanField(default=True)
#     tags = models.ManyToManyField(Tag, blank=True)
    
#     def __str__(self):
#         return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery')

    def __str__(self):
        return f"Image for {self.product.name}"

    
    
class Attribute(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_values')
    
    def __str__(self):
        return self.value