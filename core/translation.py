"""Modeltranslation registratsiya — qaysi maydonlar 3 tilda bo'lishi belgilanadi.

Har bir registratsiyadan keyin modeltranslation avtomatik tarzda
'<field>_uz_latn', '<field>_uz_cyrl', '<field>_ru' nomli yangi columnlar
yaratadi (LANGUAGES kodlari asosida). Migratsiya:
    python manage.py sync_translation_fields --noinput
"""
from modeltranslation.translator import TranslationOptions, register

from .models import (
    AwardAffiliation,
    AwardName,
    AwardType,
    Direction,
    FamilyMember,
    Representative,
)


@register(Direction)
class DirectionTR(TranslationOptions):
    fields = ('name',)


@register(AwardAffiliation)
class AwardAffiliationTR(TranslationOptions):
    fields = ('name',)


@register(AwardType)
class AwardTypeTR(TranslationOptions):
    fields = ('name',)


@register(AwardName)
class AwardNameTR(TranslationOptions):
    fields = ('name',)


@register(Representative)
class RepresentativeTR(TranslationOptions):
    fields = (
        'last_name',
        'first_name',
        'middle_name',
        'birth_place',
        'residence_place',
        'marital_status',
        'university',
        'specialty',
        'academic_degree',
        'training',
        'position',
        'career_level',
        'total_experience',
        'leadership_experience',
        'leadership_positions',
        'last_medical_treatment',
        'medical_checkup',
        'health_problems',
        'description',
        'state_events',
    )


@register(FamilyMember)
class FamilyMemberTR(TranslationOptions):
    fields = ('name', 'info', 'note')
