# Generated by Django 4.2.16 on 2024-10-18 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(default='', max_length=50, verbose_name='payment_method'),
            preserve_default=False,
        ),
    ]