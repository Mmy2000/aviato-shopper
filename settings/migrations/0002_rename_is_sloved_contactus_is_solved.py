# Generated by Django 4.2.16 on 2024-11-22 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactus',
            old_name='is_sloved',
            new_name='is_solved',
        ),
    ]
