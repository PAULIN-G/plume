from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profil


@receiver(post_save, sender=User)
def creer_ou_sauver_profil(sender, instance, created, **kwargs):
    """Crée automatiquement un Profil vide dès qu'un nouvel utilisateur est enregistré."""
    if created:
        Profil.objects.create(user=instance)
    else:
        # S'assure qu'un profil existe même pour d'anciens comptes (ex: superuser créé avant ce signal)
        Profil.objects.get_or_create(user=instance)
