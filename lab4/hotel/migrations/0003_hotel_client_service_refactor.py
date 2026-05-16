from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def forward_fill_hotels_and_clients(apps, schema_editor):
    Hotel = apps.get_model('inventory', 'Hotel')
    Room = apps.get_model('inventory', 'Room')
    Booking = apps.get_model('inventory', 'Booking')
    Client = apps.get_model('inventory', 'Client')

    default_hotel, _ = Hotel.objects.get_or_create(
        name='Default Hotel',
        defaults={'address': 'N/A', 'city': 'N/A', 'phone': ''},
    )

    Room.objects.filter(hotel__isnull=True).update(hotel=default_hotel)

    for booking in Booking.objects.all():
        email = booking.guest_email or f'guest{booking.id}@example.local'
        first_name = booking.guest_name.strip() or f'Guest{booking.id}'
        client, _ = Client.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': 'Client',
                'phone': booking.guest_phone or '',
            },
        )
        booking.client = client
        booking.save(update_fields=['client'])


def backward_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'clients',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=120)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'hotels',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='inventory.hotel')),
            ],
            options={
                'db_table': 'services',
                'ordering': ['hotel__name', 'name'],
            },
        ),
        migrations.AddField(
            model_name='room',
            name='hotel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rooms', to='inventory.hotel'),
        ),
        migrations.AddField(
            model_name='room',
            name='price_per_night',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AddField(
            model_name='booking',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='inventory.client'),
        ),
        migrations.AddField(
            model_name='booking',
            name='services',
            field=models.ManyToManyField(blank=True, related_name='bookings', to='inventory.service'),
        ),
        migrations.AddField(
            model_name='booking',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.RunPython(forward_fill_hotels_and_clients, backward_noop),
        migrations.AlterField(
            model_name='room',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rooms', to='inventory.hotel'),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='room',
            name='status',
            field=models.CharField(choices=[('AVAILABLE', 'Available'), ('MAINTENANCE', 'Maintenance')], default='AVAILABLE', max_length=20),
        ),
        migrations.AlterField(
            model_name='booking',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='inventory.client'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20),
        ),
        migrations.RemoveField(model_name='booking', name='guest_email'),
        migrations.RemoveField(model_name='booking', name='guest_name'),
        migrations.RemoveField(model_name='booking', name='guest_phone'),
        migrations.AddConstraint(
            model_name='room',
            constraint=models.UniqueConstraint(fields=('hotel', 'room_number'), name='unique_room_per_hotel'),
        ),
        migrations.AddConstraint(
            model_name='service',
            constraint=models.UniqueConstraint(fields=('hotel', 'name'), name='unique_service_name_per_hotel'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['hotel'], name='rooms_hotel_id_idx'),
        ),
    ]
