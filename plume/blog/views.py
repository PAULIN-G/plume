from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ArticleForm, CommentaireForm, InscriptionForm, ProfilForm
from .models import (
    REACTIONS_DISPONIBLES,
    Article,
    Categorie,
    Commentaire,
    Profil,
    ReactionCommentaire,
    SignalementCommentaire,
    Suivi,
    Tag,
)

ARTICLES_PAR_PAGE = 6


# --------------------------------------------------------------------------
# Authentification
# --------------------------------------------------------------------------

def inscription(request):
    if request.user.is_authenticated:
        return redirect("liste_articles")
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Ton compte a été créé.")
            return redirect("liste_articles")
    else:
        form = InscriptionForm()
    return render(request, "blog/inscription.html", {"form": form})


# --------------------------------------------------------------------------
# Liste, recherche, catégories, tags
# --------------------------------------------------------------------------

def _articles_visibles(request):
    """Articles publiés, + les brouillons de l'utilisateur connecté (pour lui seul)."""
    base = Article.objects.select_related("auteur", "categorie").prefetch_related("tags")
    if request.user.is_authenticated:
        return base.filter(Q(statut=Article.Statut.PUBLIE) | Q(auteur=request.user))
    return base.filter(statut=Article.Statut.PUBLIE)


def liste_articles(request):
    articles = _articles_visibles(request)

    q = request.GET.get("q", "").strip()
    if q:
        articles = articles.filter(
            Q(titre__icontains=q) | Q(contenu__icontains=q) | Q(resume__icontains=q)
        )

    tag_slug = request.GET.get("tag")
    tag_actif = None
    if tag_slug:
        tag_actif = get_object_or_404(Tag, slug=tag_slug)
        articles = articles.filter(tags=tag_actif)

    paginator = Paginator(articles, ARTICLES_PAR_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    articles_populaires = (
        Article.objects.filter(statut=Article.Statut.PUBLIE).order_by("-vues")[:5]
    )
    tags_populaires = Tag.objects.annotate(n=Count("articles")).order_by("-n")[:12]

    contexte = {
        "page_obj": page_obj,
        "q": q,
        "tag_actif": tag_actif,
        "articles_populaires": articles_populaires,
        "tags_populaires": tags_populaires,
    }
    return render(request, "blog/liste_articles.html", contexte)


def categorie_detail(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    articles = _articles_visibles(request).filter(categorie=categorie)
    paginator = Paginator(articles, ARTICLES_PAR_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request, "blog/categorie_detail.html", {"categorie": categorie, "page_obj": page_obj}
    )


# --------------------------------------------------------------------------
# Détail d'un article
# --------------------------------------------------------------------------

def detail_article(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("auteur", "auteur__profil", "categorie"), slug=slug
    )

    if article.est_brouillon and article.auteur != request.user:
        messages.error(request, "Cet article n'est pas encore publié.")
        return redirect("liste_articles")

    # Comptage des vues : une seule fois par visiteur et par session
    vues_deja_comptees = request.session.get("articles_vus", [])
    if article.slug not in vues_deja_comptees:
        Article.objects.filter(pk=article.pk).update(vues=article.vues + 1)
        article.vues += 1
        vues_deja_comptees.append(article.slug)
        request.session["articles_vus"] = vues_deja_comptees

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Connecte-toi pour laisser un commentaire.")
            return redirect("connexion")
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user
            parent_id = request.POST.get("parent_id")
            if parent_id:
                commentaire.parent = get_object_or_404(
                    article.commentaires, pk=parent_id
                )
            commentaire.save()
            messages.success(request, "Commentaire publié !")
            return redirect("detail_article", slug=slug)
    else:
        form = CommentaireForm()

    commentaires_racine = article.commentaires.filter(parent__isnull=True).select_related(
        "auteur"
    ).prefetch_related("reponses__auteur", "reactions", "reponses__reactions")

    articles_similaires = (
        Article.objects.filter(statut=Article.Statut.PUBLIE, categorie=article.categorie)
        .exclude(pk=article.pk)[:3]
        if article.categorie
        else Article.objects.none()
    )

    a_aime = (
        request.user.is_authenticated and article.likes.filter(pk=request.user.pk).exists()
    )
    suit_auteur = (
        request.user.is_authenticated
        and request.user != article.auteur
        and Suivi.objects.filter(suiveur=request.user, auteur_suivi=article.auteur).exists()
    )

    contexte = {
        "article": article,
        "form": form,
        "commentaires": commentaires_racine,
        "articles_similaires": articles_similaires,
        "a_aime": a_aime,
        "suit_auteur": suit_auteur,
        "reactions_disponibles": REACTIONS_DISPONIBLES,
    }
    return render(request, "blog/detail_article.html", contexte)


@login_required
@require_POST
def toggle_like(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.likes.filter(pk=request.user.pk).exists():
        article.likes.remove(request.user)
    else:
        article.likes.add(request.user)
    return redirect("detail_article", slug=slug)


# --------------------------------------------------------------------------
# CRUD Article
# --------------------------------------------------------------------------

@login_required
def creer_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.save()
            form.save_m2m()
            form._sauver_tags(article)
            if article.statut == Article.Statut.PUBLIE:
                messages.success(request, "Ton article a été publié 🎉")
            else:
                messages.success(request, "Ton brouillon a été enregistré.")
            return redirect("detail_article", slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, "blog/form_article.html", {"form": form, "action": "Nouvel article"})


@login_required
def modifier_article(request, slug):
    article = get_object_or_404(Article, slug=slug, auteur=request.user)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article mis à jour.")
            return redirect("detail_article", slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    return render(
        request, "blog/form_article.html", {"form": form, "action": "Modifier l'article", "article": article}
    )


@login_required
def supprimer_article(request, slug):
    article = get_object_or_404(Article, slug=slug, auteur=request.user)
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article supprimé.")
        return redirect("liste_articles")
    return render(request, "blog/confirmer_suppression.html", {"article": article})


# --------------------------------------------------------------------------
# Profils
# --------------------------------------------------------------------------

def profil_public(request, username):
    utilisateur = get_object_or_404(User, username=username)
    profil, _ = Profil.objects.get_or_create(user=utilisateur)
    articles = _articles_visibles(request).filter(auteur=utilisateur)
    paginator = Paginator(articles, ARTICLES_PAR_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    suit_deja = (
        request.user.is_authenticated
        and request.user != utilisateur
        and Suivi.objects.filter(suiveur=request.user, auteur_suivi=utilisateur).exists()
    )

    return render(
        request, "blog/profil_public.html",
        {
            "profil": profil,
            "auteur": utilisateur,
            "page_obj": page_obj,
            "suit_deja": suit_deja,
        },
    )


@login_required
def modifier_profil(request):
    profil, _ = Profil.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfilForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("profil_public", username=request.user.username)
    else:
        form = ProfilForm(instance=profil)
    return render(request, "blog/modifier_profil.html", {"form": form})


@login_required
@require_POST
def toggle_follow(request, username):
    auteur = get_object_or_404(User, username=username)
    if auteur == request.user:
        messages.error(request, "Tu ne peux pas te suivre toi-même 😄")
        return redirect("profil_public", username=username)

    suivi, cree = Suivi.objects.get_or_create(suiveur=request.user, auteur_suivi=auteur)
    if not cree:
        suivi.delete()
        messages.info(request, f"Tu ne suis plus {auteur.username}.")
    else:
        messages.success(request, f"Tu suis maintenant {auteur.username} !")
    return redirect("profil_public", username=username)


@login_required
def tableau_de_bord(request):
    """Statistiques personnelles de l'auteur connecté : vues, likes, commentaires par article."""
    articles = (
        Article.objects.filter(auteur=request.user)
        .order_by("-date_publication")
    )
    total_vues = sum(a.vues for a in articles)
    total_likes = sum(a.nombre_likes for a in articles)
    total_commentaires = Commentaire.objects.filter(article__auteur=request.user).count()
    total_suiveurs = request.user.suivi_par.count()

    contexte = {
        "articles": articles,
        "total_vues": total_vues,
        "total_likes": total_likes,
        "total_commentaires": total_commentaires,
        "total_suiveurs": total_suiveurs,
    }
    return render(request, "blog/tableau_de_bord.html", contexte)


# --------------------------------------------------------------------------
# Réactions & signalement sur les commentaires
# --------------------------------------------------------------------------

@login_required
@require_POST
def reagir_commentaire(request, pk):
    commentaire = get_object_or_404(Commentaire, pk=pk)
    emoji = request.POST.get("emoji")
    emojis_valides = [code for code, _ in REACTIONS_DISPONIBLES]
    if emoji in emojis_valides:
        reaction, cree = ReactionCommentaire.objects.get_or_create(
            commentaire=commentaire, utilisateur=request.user, emoji=emoji
        )
        if not cree:
            reaction.delete()
    return redirect("detail_article", slug=commentaire.article.slug)


@login_required
@require_POST
def signaler_commentaire(request, pk):
    commentaire = get_object_or_404(Commentaire, pk=pk)
    raison = request.POST.get("raison", "").strip()
    _, cree = SignalementCommentaire.objects.get_or_create(
        commentaire=commentaire, utilisateur=request.user, defaults={"raison": raison}
    )
    if cree:
        messages.success(request, "Merci, ce commentaire a été signalé aux modérateurs.")
    else:
        messages.info(request, "Tu as déjà signalé ce commentaire.")
    return redirect("detail_article", slug=commentaire.article.slug)


# --------------------------------------------------------------------------
# SEO : robots.txt (le sitemap et le flux RSS sont dans leurs propres modules)
# --------------------------------------------------------------------------

def robots_txt(request):
    from django.http import HttpResponse

    lignes = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lignes), content_type="text/plain")
