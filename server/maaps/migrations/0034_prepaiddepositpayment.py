# Generated by Django 3.1.7 on 2021-07-13 00:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maaps', '0033_auto_20210523_0311'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrepaidDepositPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('value', models.FloatField(default=0)),
                ('for_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prepaidDepositPaymentsForOther', to=settings.AUTH_USER_MODEL, verbose_name='Für Benutzer')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prepaidDepositPayments', to='maaps.invoice')),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prepaidDepositPayments', to='maaps.transaction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prepaidDepositPayments', to=settings.AUTH_USER_MODEL, verbose_name='Benutzer')),
            ],
        ),
    ]