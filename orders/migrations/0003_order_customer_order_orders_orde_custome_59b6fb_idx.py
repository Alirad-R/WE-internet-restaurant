# Generated by Django 5.2.1 on 2025-07-25 12:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coupons", "0005_couponusage_coupons_cou_used_at_2fc071_idx"),
        ("orders", "0002_order_coupon"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="customer",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["customer"], name="orders_orde_custome_59b6fb_idx"
            ),
        ),
    ]
