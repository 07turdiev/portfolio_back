"""Data migration: mukofotlar iyerarxiyasi (mansublik / tur / nom)."""
from django.core.management import call_command
from django.db import migrations


def seed(apps, schema_editor):
    call_command('populate_awards', verbosity=0)


def unseed(apps, schema_editor):
    apps.get_model('core', 'AwardName').objects.all().delete()
    apps.get_model('core', 'AwardType').objects.all().delete()
    apps.get_model('core', 'AwardAffiliation').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_seed_directions'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
