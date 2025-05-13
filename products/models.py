from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='categories/images', blank=True, null=True)
    
    def __str__(self):
        return self.name
class Tag(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/images', blank=True, null=True)
    stock = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    def __str__(self):
        return self.name
    
    
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