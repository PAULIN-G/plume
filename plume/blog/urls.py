from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.liste_articles, name="liste_articles"),
    path("categorie/<slug:slug>/", views.categorie_detail, name="categorie_detail"),

    path("article/nouveau/", views.creer_article, name="creer_article"),
    path("article/<slug:slug>/", views.detail_article, name="detail_article"),
    path("article/<slug:slug>/modifier/", views.modifier_article, name="modifier_article"),
    path("article/<slug:slug>/supprimer/", views.supprimer_article, name="supprimer_article"),
    path("article/<slug:slug>/like/", views.toggle_like, name="toggle_like"),

    path("auteur/<str:username>/", views.profil_public, name="profil_public"),
    path("auteur/<str:username>/suivre/", views.toggle_follow, name="toggle_follow"),
    path("profil/modifier/", views.modifier_profil, name="modifier_profil"),
    path("tableau-de-bord/", views.tableau_de_bord, name="tableau_de_bord"),

    path("commentaire/<int:pk>/reagir/", views.reagir_commentaire, name="reagir_commentaire"),
    path("commentaire/<int:pk>/signaler/", views.signaler_commentaire, name="signaler_commentaire"),

    path("inscription/", views.inscription, name="inscription"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="blog/connexion.html"),
        name="connexion",
    ),
    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(next_page="liste_articles"),
        name="deconnexion",
    ),
    path(
        "mot-de-passe/modifier/",
        auth_views.PasswordChangeView.as_view(
            template_name="blog/mot_de_passe_modifier.html",
            success_url="/mot-de-passe/modifie/",
        ),
        name="password_change",
    ),
    path(
        "mot-de-passe/modifie/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="blog/mot_de_passe_modifie.html"
        ),
        name="password_change_done",
    ),
]
