# Generated by Django 3.1.7 on 2021-07-14 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0036_auto_20210713_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='type',
            field=models.CharField(blank=True, default='receipt', max_length=100, null=True),
        ),
    ]