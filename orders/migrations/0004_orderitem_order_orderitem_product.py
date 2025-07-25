# Generated by Django 5.2.1 on 2025-07-25 12:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_order_customer_order_orders_orde_custome_59b6fb_idx"),
        ("products", "0004_product_image_alter_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="orders.order",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="products.product",
            ),
            preserve_default=False,
        ),
    ]
