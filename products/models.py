from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/images', blank=True, null=True)
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
