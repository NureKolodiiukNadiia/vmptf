from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_seed_services'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='created_by',
        ),
    ]
