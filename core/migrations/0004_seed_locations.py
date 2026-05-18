"""Data migration: viloyat / tuman / mahalla ma'lumotlarini avtomatik yuklash.

Bu migratsiya `populate_locations` management komandasini chaqiradi.
Server-ga push qilingach `python manage.py migrate` o'z-o'zidan ishga tushiradi.
"""
from django.core.management import call_command
from django.db import migrations


def seed_locations(apps, schema_editor):
    call_command('populate_locations', verbosity=0)


def unseed_locations(apps, schema_editor):
    Mahalla = apps.get_model('core', 'Mahalla')
    District = apps.get_model('core', 'District')
    Region = apps.get_model('core', 'Region')
    Mahalla.objects.all().delete()
    District.objects.all().delete()
    Region.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_district_region_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_locations, unseed_locations),
    ]
