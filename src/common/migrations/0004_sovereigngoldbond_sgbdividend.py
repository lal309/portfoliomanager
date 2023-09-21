# Generated by Django 4.1.10 on 2023-09-18 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_preferences_investment_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='SovereignGoldBond',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tranche', models.CharField(max_length=30, unique=True)),
                ('date_subscription', models.DateField(verbose_name='Subscription Date')),
                ('date_issuance', models.DateField(verbose_name='Issuance Date')),
                ('issue_price', models.DecimalField(decimal_places=10, max_digits=30, verbose_name='Price')),
                ('issue_price_online', models.DecimalField(decimal_places=10, max_digits=30, verbose_name='Online Price')),
                ('date_maturity', models.DateField(verbose_name='Maturity Date')),
                ('min_weight_gram', models.IntegerField()),
                ('max_weight_gram', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SGBDividend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('date', models.DateField()),
                ('sgb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.sovereigngoldbond')),
            ],
            options={
                'unique_together': {('sgb', 'date')},
            },
        ),
    ]
