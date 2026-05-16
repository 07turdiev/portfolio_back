"""Jazzmin bilan admin paneli."""
from datetime import date

from django.contrib import admin
from django.db.models import CharField as DjangoCharField
from django.db.models import TextField as DjangoTextField
from django.forms import Select, Textarea, TextInput
from django.utils.html import format_html

from .models import (
    AwardAffiliation,
    AwardName,
    AwardType,
    Direction,
    FamilyMember,
    Language,
    Representative,
    RepresentativeAward,
)


# ── Tillar ────────────────────────────────────────────────────────────────

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('order', 'code', 'name')
    list_display_links = ('code', 'name')
    list_editable = ('order',)
    search_fields = ('code', 'name')
    ordering = ('order', 'name')
    prepopulated_fields = {'code': ('name',)}


# ── Yo'nalishlar ──────────────────────────────────────────────────────────

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('order', 'key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru', 'icon',
                    'representatives_count')
    list_display_links = ('key', 'name_uz_latn')
    list_editable = ('order',)
    search_fields = ('key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    ordering = ('order', 'key')
    prepopulated_fields = {'key': ('name_uz_latn',)}

    @admin.display(description='Vakillar soni')
    def representatives_count(self, obj):
        return obj.representatives.filter(is_active=True).count()


# ── Mukofotlar ────────────────────────────────────────────────────────────

class AwardTypeInline(admin.TabularInline):
    model = AwardType
    extra = 0
    fields = ('order', 'key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    prepopulated_fields = {'key': ('name_uz_latn',)}
    show_change_link = True


@admin.register(AwardAffiliation)
class AwardAffiliationAdmin(admin.ModelAdmin):
    list_display = ('order', 'key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru',
                    'types_count')
    list_display_links = ('key', 'name_uz_latn')
    list_editable = ('order',)
    search_fields = ('key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    ordering = ('order', 'key')
    prepopulated_fields = {'key': ('name_uz_latn',)}
    inlines = [AwardTypeInline]

    @admin.display(description='Turlar soni')
    def types_count(self, obj):
        return obj.types.count()


class AwardNameInline(admin.TabularInline):
    model = AwardName
    extra = 0
    fields = ('order', 'key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    prepopulated_fields = {'key': ('name_uz_latn',)}
    show_change_link = True


@admin.register(AwardType)
class AwardTypeAdmin(admin.ModelAdmin):
    list_display = ('affiliation', 'order', 'key', 'name_uz_latn', 'names_count')
    list_display_links = ('key', 'name_uz_latn')
    list_editable = ('order',)
    list_filter = ('affiliation',)
    search_fields = ('key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    ordering = ('affiliation', 'order', 'key')
    autocomplete_fields = ('affiliation',)
    prepopulated_fields = {'key': ('name_uz_latn',)}
    inlines = [AwardNameInline]

    @admin.display(description='Nomlar soni')
    def names_count(self, obj):
        return obj.names.count()


@admin.register(AwardName)
class AwardNameAdmin(admin.ModelAdmin):
    list_display = ('order', 'key', 'name_uz_latn', 'type', 'affiliation_display')
    list_display_links = ('key', 'name_uz_latn')
    list_editable = ('order',)
    list_filter = ('type__affiliation', 'type')
    search_fields = ('key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    ordering = ('type__affiliation', 'type', 'order', 'key')
    autocomplete_fields = ('type',)
    prepopulated_fields = {'key': ('name_uz_latn',)}

    @admin.display(description='Mansubligi', ordering='type__affiliation')
    def affiliation_display(self, obj):
        return obj.type.affiliation


# ── Vakillar ──────────────────────────────────────────────────────────────

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1
    fields = ('order', 'relation', 'name', 'info', 'note')
    ordering = ('order', 'id')


class RepresentativeAwardInline(admin.TabularInline):
    model = RepresentativeAward
    extra = 1
    fields = ('award', 'year')
    autocomplete_fields = ('award',)
    ordering = ('-year',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'year':
            current = date.today().year
            choices = [('', '—')] + [
                (y, str(y)) for y in range(current + 1, 1939, -1)
            ]
            formfield.widget = Select(choices=choices)
        return formfield


@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    # ── Ro'yxat ko'rinishi ────────────────────────────────────────────────
    list_display = (
        'photo_thumb',
        'full_name_col',
        'direction_badge',
        'gender_badge',
        'position',
        'birth_date',
        'awards_count_badge',
        'active_badge',
    )
    list_display_links = ('photo_thumb', 'full_name_col')
    list_filter = ('direction', 'gender', 'is_active', 'nationality')
    search_fields = (
        'first_name', 'last_name', 'middle_name',
        'position', 'birth_place', 'residence_place',
    )
    ordering = ('last_name', 'first_name')
    list_per_page = 30
    list_select_related = ('direction',)
    date_hierarchy = 'birth_date'
    save_on_top = True
    show_full_result_count = False

    # ── Tahrirlash sahifasi ──────────────────────────────────────────────
    autocomplete_fields = ('direction',)
    filter_horizontal = ('languages',)
    inlines = [FamilyMemberInline, RepresentativeAwardInline]

    # Barcha CharField/TextField inputlari forma ustunini to'liq egallaydi
    formfield_overrides = {
        DjangoCharField: {
            'widget': TextInput(
                attrs={'style': 'width: 100%; max-width: 700px;'}
            )
        },
        DjangoTextField: {
            'widget': Textarea(
                attrs={
                    'style': 'width: 100%; max-width: 900px; min-height: 140px;',
                    'rows': 6,
                }
            )
        },
    }

    fieldsets = (
        ("Shaxsiy ma'lumotlar", {
            'fields': (
                'direction',
                'is_active',
                'photo',
                'last_name',
                'first_name',
                'middle_name',
                'gender',
                'nationality',
                'birth_date',
                'birth_place',
                'residence_place',
            ),
        }),
        ("Oilasi haqida", {
            'fields': ('marital_status',),
        }),
        ("Ma'lumoti (ta'lim)", {
            'fields': (
                'university',
                'specialty',
                'academic_degree',
                'languages',
                'training',
            ),
        }),
        ('Mehnat faoliyati', {
            'fields': (
                'position',
                'career_level',
                'total_experience',
                'leadership_experience',
                'leadership_positions',
            ),
        }),
        ("Sog'lig'i", {
            'fields': (
                'health',
                'last_medical_treatment',
                'medical_checkup',
                'health_problems',
            ),
        }),
        ('Faoliyati haqida', {
            'fields': (
                'description',
                'state_events',
            ),
        }),
    )

    # ── Ro'yxat ustunlari ────────────────────────────────────────────────

    @admin.display(description='Surat')
    def photo_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:42px;height:50px;object-fit:cover;'
                'border-radius:4px;border:1px solid #e5e7eb"/>',
                obj.photo.url,
            )
        return format_html(
            '<div style="width:42px;height:50px;background:#f3f4f6;'
            'border:1px dashed #d1d5db;border-radius:4px;display:flex;'
            'align-items:center;justify-content:center;color:#9ca3af;'
            'font-size:18px">👤</div>'
        )

    @admin.display(description='Ismi sharifi', ordering='last_name')
    def full_name_col(self, obj):
        return format_html(
            '<strong>{}</strong>',
            obj.full_name,
        )

    @admin.display(description="Yo'nalishi", ordering='direction')
    def direction_badge(self, obj):
        return format_html(
            '<span style="background:#e0e7ff;color:#3730a3;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;'
            'white-space:nowrap">{}</span>',
            obj.direction.name_uz_latn,
        )

    @admin.display(description='Jinsi', ordering='gender')
    def gender_badge(self, obj):
        if obj.gender == Representative.GENDER_MALE:
            return format_html(
                '<span style="color:#2563eb;font-weight:600">♂ Erkak</span>'
            )
        return format_html(
            '<span style="color:#db2777;font-weight:600">♀ Ayol</span>'
        )

    @admin.display(description='Mukofotlari')
    def awards_count_badge(self, obj):
        n = obj.representative_awards.count()
        if not n:
            return format_html('<span style="color:#9ca3af">—</span>')
        return format_html(
            '<span style="background:#fef3c7;color:#92400e;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700">🏆 {}</span>',
            n,
        )

    @admin.display(description='Holat', ordering='is_active')
    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#10b981;color:white;padding:3px 10px;'
                'border-radius:12px;font-size:11px;font-weight:700">FAOL</span>'
            )
        return format_html(
            '<span style="background:#9ca3af;color:white;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700">NOFAOL</span>'
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('direction')
            .prefetch_related('representative_awards')
        )


# Note: RepresentativeAward menyuda alohida ko'rinmaydi —
# u Vakil tahrirlash sahifasi ichida inline sifatida qo'shiladi.
