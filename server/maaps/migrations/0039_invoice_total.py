# Generated by Django 3.1.7 on 2021-07-14 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0038_machine_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='total',
            field=models.FloatField(default=0),
        ),
    ]
