from decimal import Decimal

from django.db import migrations


def seed_services(apps, schema_editor):
    Hotel = apps.get_model('inventory', 'Hotel')
    Service = apps.get_model('inventory', 'Service')

    defaults = [
        ('Breakfast', 'Daily breakfast package', Decimal('15.00')),
        ('Airport Transfer', 'One-way transfer between airport and hotel', Decimal('30.00')),
        ('Spa Access', 'Daily access to spa zone', Decimal('25.00')),
    ]

    for hotel in Hotel.objects.all():
        for name, description, price in defaults:
            Service.objects.get_or_create(
                hotel=hotel,
                name=name,
                defaults={'description': description, 'price': price},
            )


def unseed_services(apps, schema_editor):
    Service = apps.get_model('inventory', 'Service')
    Service.objects.filter(name__in=['Breakfast', 'Airport Transfer', 'Spa Access']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_hotel_client_service_refactor'),
    ]

    operations = [
        migrations.RunPython(seed_services, unseed_services),
    ]
