from django.contrib import admin

from .models import (
    Article,
    Categorie,
    Commentaire,
    Profil,
    ReactionCommentaire,
    SignalementCommentaire,
    Suivi,
    Tag,
)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug", "couleur")
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug")
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "auteur", "categorie", "statut", "vues", "date_publication")
    list_filter = ("statut", "categorie", "auteur")
    search_fields = ("titre", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    autocomplete_fields = ("auteur",)
    filter_horizontal = ("tags", "likes")


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ("article", "auteur", "parent", "nombre_signalements", "date_creation")
    list_filter = ("date_creation",)
    search_fields = ("contenu",)


@admin.register(SignalementCommentaire)
class SignalementCommentaireAdmin(admin.ModelAdmin):
    list_display = ("commentaire", "utilisateur", "raison", "date_creation")
    list_filter = ("date_creation",)
    search_fields = ("raison", "commentaire__contenu")


@admin.register(ReactionCommentaire)
class ReactionCommentaireAdmin(admin.ModelAdmin):
    list_display = ("commentaire", "utilisateur", "emoji", "date_creation")
    list_filter = ("emoji", "date_creation")


@admin.register(Suivi)
class SuiviAdmin(admin.ModelAdmin):
    list_display = ("suiveur", "auteur_suivi", "date_creation")
    search_fields = ("suiveur__username", "auteur_suivi__username")


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("user", "site_web")
    search_fields = ("user__username",)
