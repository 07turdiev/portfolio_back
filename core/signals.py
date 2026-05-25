"""Cache invalidatsiya signallari.

Admin orqali modellar o'zgarganda tegishli cache kalitlarini tozalaymiz, shunda
foydalanuvchi keyingi so'rovda yangi qiymatlarni darhol ko'radi.
"""
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import (
    AwardAffiliation,
    AwardName,
    AwardType,
    Direction,
    District,
    InfoCard,
    Mahalla,
    Region,
    Representative,
)


def _clear_directions():
    cache.delete('directions:list:v1')


def _clear_awards():
    cache.delete('awards:taxonomy:v1')


def _clear_info_cards():
    cache.delete('info_cards:list:v1')


def _clear_locations():
    # Variantlar ko'p — pattern bo'yicha o'chirish locmem'da qo'llanmaydi.
    # Shu sababli kalitlarni `cache.delete_many` bilan ro'yxat qilamiz va
    # `mahallas` per-tin kalitlarini soatdan keyin TTL o'z-o'zidan tozalashga
    # qoldiramiz (chunki ularda district yaqinda o'zgarmaydi).
    keys = ['locations:regions:v1', 'locations:districts:v1:all']
    cache.delete_many(keys)


# ── Direction ────────────────────────────────────────────────────────────
@receiver([post_save, post_delete], sender=Direction)
@receiver([post_save, post_delete], sender=Representative)
def _on_direction_or_rep_change(sender, **kwargs):
    _clear_directions()


# ── Awards taxonomy ──────────────────────────────────────────────────────
@receiver([post_save, post_delete], sender=AwardAffiliation)
@receiver([post_save, post_delete], sender=AwardType)
@receiver([post_save, post_delete], sender=AwardName)
def _on_award_change(sender, **kwargs):
    _clear_awards()


# ── Info cards ───────────────────────────────────────────────────────────
@receiver([post_save, post_delete], sender=InfoCard)
def _on_info_card_change(sender, **kwargs):
    _clear_info_cards()


# ── Locations ────────────────────────────────────────────────────────────
@receiver([post_save, post_delete], sender=Region)
@receiver([post_save, post_delete], sender=District)
@receiver([post_save, post_delete], sender=Mahalla)
def _on_location_change(sender, **kwargs):
    _clear_locations()
