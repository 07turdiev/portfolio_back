"""Jazzmin bilan admin paneli."""
import json
from datetime import date

from django import forms
from django.contrib import admin
from django.db.models import CharField as DjangoCharField
from django.db.models import TextField as DjangoTextField
from django.forms import Select, Textarea, TextInput
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from .models import (
    AwardAffiliation,
    AwardName,
    AwardType,
    Direction,
    District,
    FamilyMember,
    Language,
    Mahalla,
    Region,
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
class DirectionAdmin(TabbedTranslationAdmin):
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

class AwardTypeInline(TranslationTabularInline):
    model = AwardType
    extra = 0
    fields = ('order', 'key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    prepopulated_fields = {'key': ('name_uz_latn',)}
    show_change_link = True


@admin.register(AwardAffiliation)
class AwardAffiliationAdmin(TabbedTranslationAdmin):
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


class AwardNameInline(TranslationTabularInline):
    model = AwardName
    extra = 0
    fields = ('order', 'key', 'name_uz_latn', 'name_uz_cyrl', 'name_ru')
    prepopulated_fields = {'key': ('name_uz_latn',)}
    show_change_link = True


@admin.register(AwardType)
class AwardTypeAdmin(TabbedTranslationAdmin):
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
class AwardNameAdmin(TabbedTranslationAdmin):
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

class FamilyMemberInline(TranslationTabularInline):
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


class RepresentativeForm(forms.ModelForm):
    """Cascading region → district → mahalla dropdownlar.

    region va district modelda yo'q — faqat UX uchun virtual maydonlar.
    Saqlashda residence_mahalla ishlatiladi (district/region undan kelib chiqadi).
    """

    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('name_uz_latn'),
        label="Viloyat",
        required=False,
        widget=forms.Select(attrs={'id': 'id_region'}),
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        label="Tuman",
        required=False,
        widget=forms.Select(attrs={'id': 'id_district'}),
    )

    class Meta:
        model = Representative
        fields = '__all__'
        widgets = {
            'residence_mahalla': forms.Select(attrs={'id': 'id_residence_mahalla'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mahalla querysetini boshlang'ich holatda bo'sh qilish
        self.fields['residence_mahalla'].queryset = Mahalla.objects.none()

        # POST yuborilganda — qaytadan tanlanganga qarab queryset qurish
        if self.data.get('region'):
            try:
                region_id = self.data.get('region')
                self.fields['district'].queryset = District.objects.filter(
                    region_id=region_id
                ).order_by('name_uz_latn')
            except (ValueError, TypeError):
                pass

        if self.data.get('district'):
            try:
                district_id = self.data.get('district')
                self.fields['residence_mahalla'].queryset = Mahalla.objects.filter(
                    district_id=district_id
                ).order_by('name_uz_latn')
            except (ValueError, TypeError):
                pass

        # Edit holati — instance.residence_mahalla bor bo'lsa
        if self.instance and self.instance.pk and self.instance.residence_mahalla_id:
            mahalla = self.instance.residence_mahalla
            district = mahalla.district
            region = district.region
            self.fields['region'].initial = region.soato
            self.fields['district'].initial = district.soato
            if not self.data:
                # GET (POST emas) — querysetlarni instance asosida to'ldiramiz
                self.fields['district'].queryset = District.objects.filter(
                    region=region
                ).order_by('name_uz_latn')
                self.fields['residence_mahalla'].queryset = Mahalla.objects.filter(
                    district=district
                ).order_by('name_uz_latn')


@admin.register(Representative)
class RepresentativeAdmin(TabbedTranslationAdmin):
    form = RepresentativeForm
    change_form_template = 'admin/core/representative/change_form.html'

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
                'region',
                'district',
                'residence_mahalla',
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
            .select_related('direction', 'residence_mahalla__district__region')
            .prefetch_related('representative_awards')
        )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Cascading dropdown uchun districts/mahallas JSON ni template'ga uzatish."""
        extra_context = extra_context or {}

        # Tumanlar — viloyat SOATO bo'yicha guruhlangan
        districts_by_region = {}
        for d in District.objects.all().order_by('name_uz_latn'):
            districts_by_region.setdefault(d.region_id, []).append(
                {'id': d.soato, 'name': d.name_uz_latn}
            )

        # Mahallalar — tuman SOATO bo'yicha guruhlangan
        mahallas_by_district = {}
        for m in Mahalla.objects.all().order_by('name_uz_latn'):
            mahallas_by_district.setdefault(m.district_id, []).append(
                {'id': m.tin, 'name': m.name_uz_latn}
            )

        extra_context['districts_json'] = json.dumps(districts_by_region)
        extra_context['mahallas_json'] = json.dumps(mahallas_by_district)
        return super().changeform_view(request, object_id, form_url, extra_context)


# Note: RepresentativeAward menyuda alohida ko'rinmaydi —
# u Vakil tahrirlash sahifasi ichida inline sifatida qo'shiladi.


# ── Hududiy bo'linish ─────────────────────────────────────────────────────

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('soato', 'name_uz_latn', 'name_uz_cyrl', 'name_ru', 'slug',
                    'districts_count', 'residents_count')
    search_fields = ('name_uz_latn', 'name_uz_cyrl', 'name_ru', 'slug', 'soato')
    ordering = ('name_uz_latn',)

    @admin.display(description='Tumanlar soni')
    def districts_count(self, obj):
        return obj.districts.count()

    @admin.display(description='Vakillar soni')
    def residents_count(self, obj):
        return Representative.objects.filter(
            residence_mahalla__district__region=obj, is_active=True
        ).count()


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('soato', 'name_uz_latn', 'region', 'mahallas_count',
                    'residents_count')
    list_filter = ('region',)
    list_select_related = ('region',)
    search_fields = ('name_uz_latn', 'name_uz_cyrl', 'name_ru', 'soato')
    autocomplete_fields = ('region',)
    ordering = ('region', 'name_uz_latn')

    @admin.display(description='Mahallalar soni')
    def mahallas_count(self, obj):
        return obj.mahallas.count()

    @admin.display(description='Vakillar soni')
    def residents_count(self, obj):
        return Representative.objects.filter(
            residence_mahalla__district=obj, is_active=True
        ).count()


@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    list_display = ('tin', 'name_uz_latn', 'district_col', 'region_col')
    list_filter = ('district__region',)
    list_select_related = ('district', 'district__region')
    search_fields = (
        'name_uz_latn', 'name_uz_cyrl', 'name_ru', 'tin', 'code',
        'district__name_uz_latn', 'district__region__name_uz_latn',
    )
    autocomplete_fields = ('district',)
    ordering = ('district', 'name_uz_latn')

    @admin.display(description='Tumani', ordering='district__name_uz_latn')
    def district_col(self, obj):
        return obj.district.name_uz_latn

    @admin.display(description='Viloyati', ordering='district__region__name_uz_latn')
    def region_col(self, obj):
        return obj.district.region.name_uz_latn
