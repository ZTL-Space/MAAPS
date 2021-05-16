# Generated by Django 3.1.7 on 2021-05-16 01:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maaps', '0026_invoice_due'),
    ]

    operations = [
        migrations.AddField(
            model_name='spacerentpayment',
            name='for_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spaceRentPaymentsForOther', to=settings.AUTH_USER_MODEL, verbose_name='Für Benutzer'),
        ),
    ]