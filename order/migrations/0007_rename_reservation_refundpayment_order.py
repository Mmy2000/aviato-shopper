# Generated by Django 4.2.16 on 2025-05-19 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_refundpayment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refundpayment',
            old_name='reservation',
            new_name='order',
        ),
    ]
