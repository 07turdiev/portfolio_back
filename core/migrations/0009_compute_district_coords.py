"""Data migration: tumanlar uchun lat/lng (centroid) ni avtomatik hisoblaydi."""
from django.core.management import call_command
from django.db import migrations


def compute(apps, schema_editor):
    call_command('compute_district_coords', verbosity=0)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_district_lat_district_lng'),
    ]

    operations = [
        migrations.RunPython(compute, noop),
    ]
