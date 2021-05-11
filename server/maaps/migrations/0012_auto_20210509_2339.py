# Generated by Django 3.1.7 on 2021-05-09 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0011_auto_20210509_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='profile',
            name='postalcode',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='street',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]