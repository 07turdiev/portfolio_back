"""Data migration: chet tillar ro'yxati."""
from django.core.management import call_command
from django.db import migrations


def seed(apps, schema_editor):
    call_command('populate_languages', verbosity=0)


def unseed(apps, schema_editor):
    apps.get_model('core', 'Language').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_seed_locations'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
