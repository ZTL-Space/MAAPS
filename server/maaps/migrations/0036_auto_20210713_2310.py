# Generated by Django 3.1.7 on 2021-07-13 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0035_auto_20210713_0050'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='allow_invoice',
            new_name='allow_postpaid',
        ),
    ]
