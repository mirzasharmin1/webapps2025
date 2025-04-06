# Generated by Django 5.1.7 on 2025-04-02 00:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('GBP', 'GB Pounds (£)'), ('USD', 'US Dollars ($)'), ('EUR', 'Euros (€)')], default='GBP', max_length=3)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.CharField(blank=True, max_length=30, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
