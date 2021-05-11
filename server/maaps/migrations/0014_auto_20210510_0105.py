# Generated by Django 3.1.7 on 2021-05-10 01:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0013_auto_20210509_2342'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialpayment',
            name='machinesession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='materialpayments', to='maaps.machinesession'),
        ),
        migrations.AddField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='machinesessionpayment',
            name='end',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='machinesessionpayment',
            name='start',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]