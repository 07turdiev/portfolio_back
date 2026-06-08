# Vakil tug'ilgan/yashash joyini mahalla darajasidan tuman darajasiga o'tkazish.
# Mavjud ma'lumotlar saqlanadi: har bir mahalla o'z tumaniga ko'chiriladi.
import django.db.models.deletion
from django.db import migrations, models


def mahalla_to_district(apps, schema_editor):
    Representative = apps.get_model('core', 'Representative')
    Mahalla = apps.get_model('core', 'Mahalla')
    district_of = dict(Mahalla.objects.values_list('tin', 'district_id'))

    for rep in Representative.objects.all().only(
        'id', 'birth_mahalla_id', 'residence_mahalla_id',
        'birth_district_id', 'residence_district_id',
    ):
        changed = False
        if rep.birth_mahalla_id and not rep.birth_district_id:
            rep.birth_district_id = district_of.get(rep.birth_mahalla_id)
            changed = True
        if rep.residence_mahalla_id and not rep.residence_district_id:
            rep.residence_district_id = district_of.get(rep.residence_mahalla_id)
            changed = True
        if changed:
            rep.save(update_fields=['birth_district_id', 'residence_district_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_representative_birth_place_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='representative',
            name='birth_district',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='born_residents', to='core.district',
                verbose_name="Tug'ilgan joyi (tuman)",
                help_text='Viloyat → tuman tanlanadi.',
            ),
        ),
        migrations.AddField(
            model_name='representative',
            name='residence_district',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='residents', to='core.district',
                verbose_name='Hozirgi yashash joyi (tuman)',
                help_text='Viloyat → tuman tanlanadi. Xaritada marker shu tumanga qo\'yiladi.',
            ),
        ),
        migrations.RunPython(mahalla_to_district, noop),
        migrations.RemoveField(
            model_name='representative',
            name='birth_mahalla',
        ),
        migrations.RemoveField(
            model_name='representative',
            name='residence_mahalla',
        ),
        migrations.AlterField(
            model_name='representative',
            name='residence_place',
            field=models.CharField(
                blank=True, max_length=200,
                verbose_name="Yashash manzili (qo'shimcha)",
                help_text="Tumandan tashqari aniqlashtirish: mahalla, ko'cha, uy raqami",
            ),
        ),
    ]
