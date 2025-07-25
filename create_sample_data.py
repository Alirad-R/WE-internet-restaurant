#!/usr/bin/env python
"""
Script to create sample data for testing product-images endpoint
Run this after starting the Django shell: python manage.py shell < create_sample_data.py
"""

from products.models import Product, Category, Tag, ProductImage
from accounts.models import User

# Create sample categories
print("Creating sample categories...")
categories = []
category_data = [
    {'name': 'Beverages', 'description': 'Hot and cold drinks'},
    {'name': 'Main Dishes', 'description': 'Hearty meals and entrees'},
    {'name': 'Desserts', 'description': 'Sweet treats and desserts'},
]

for cat_data in category_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories.append(category)
    print(f"{'Created' if created else 'Found'} category: {category.name}")

# Create sample tags
print("\nCreating sample tags...")
tag_names = ['spicy', 'vegetarian', 'gluten-free', 'popular', 'new']
tags = []
for tag_name in tag_names:
    tag, created = Tag.objects.get_or_create(name=tag_name)
    tags.append(tag)
    print(f"{'Created' if created else 'Found'} tag: {tag.name}")

# Create sample products
print("\nCreating sample products...")
products_data = [
    {
        'name': 'Espresso Coffee',
        'description': 'Rich and bold espresso coffee',
        'price': 250,
        'category': categories[0],  # Beverages
        'is_featured': True,
        'tags': [tags[3]]  # popular
    },
    {
        'name': 'Grilled Chicken Burger',
        'description': 'Juicy grilled chicken with lettuce and tomato',
        'price': 850,
        'category': categories[1],  # Main Dishes
        'is_featured': True,
        'tags': [tags[3]]  # popular
    },
    {
        'name': 'Chocolate Cake',
        'description': 'Decadent chocolate cake with cream frosting',
        'price': 450,
        'category': categories[2],  # Desserts
        'tags': [tags[4]]  # new
    },
    {
        'name': 'Veggie Salad',
        'description': 'Fresh mixed vegetables with olive oil dressing',
        'price': 380,
        'category': categories[1],  # Main Dishes
        'tags': [tags[1], tags[2]]  # vegetarian, gluten-free
    },
]

products = []
for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        defaults={
            'description': prod_data['description'],
            'price': prod_data['price'],
            'category': prod_data['category'],
            'is_featured': prod_data.get('is_featured', False),
        }
    )
    
    # Add tags
    if 'tags' in prod_data:
        product.tags.set(prod_data['tags'])
    
    products.append(product)
    print(f"{'Created' if created else 'Found'} product: {product.name} (ID: {product.id})")

print(f"\nSample data creation complete!")
print(f"Created {len(categories)} categories, {len(tags)} tags, {len(products)} products")
print("\nYou can now test the product-images endpoint with these product IDs:")
for product in products:
    print(f"  - Product ID {product.id}: {product.name}")

print("\nExample API calls:")
print("  GET  http://localhost:8000/api/products/product-images/")
print("  POST http://localhost:8000/api/products/product-images/")
print("       (with form-data: product=1, image=<file>)") 