"""Data migration: 5 ta yo'nalish (theater_circus, education, heritage, cinema, concert)."""
from django.core.management import call_command
from django.db import migrations


def seed(apps, schema_editor):
    call_command('populate_directions', verbosity=0)


def unseed(apps, schema_editor):
    apps.get_model('core', 'Direction').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_seed_languages'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
