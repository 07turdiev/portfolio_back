"""Data migration: tumanlarning 3 tilli nomlari + slug ni to'ldiradi."""
from django.core.management import call_command
from django.db import migrations


def seed(apps, schema_editor):
    call_command('populate_district_names', verbosity=0)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_compute_district_coords'),
    ]

    operations = [
        migrations.RunPython(seed, noop),
    ]
