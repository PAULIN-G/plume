import math

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def _slug_unique(modele, valeur_base, instance_pk=None):
    """Génère un slug unique pour un modèle donné, en ajoutant -2, -3... si besoin."""
    base = slugify(valeur_base) or "item"
    slug = base
    n = 1
    qs = modele.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=slug).exists():
        n += 1
        slug = f"{base}-{n}"
    return slug


class Categorie(models.Model):
    nom = models.CharField("Nom", max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    couleur = models.CharField(
        "Couleur (hex)", max_length=7, default="#6366f1",
        help_text="Couleur du badge de catégorie, ex : #6366f1",
    )

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unique(Categorie, self.nom, self.pk)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("categorie_detail", kwargs={"slug": self.slug})


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unique(Tag, self.nom, self.pk)
        super().save(*args, **kwargs)


class Profil(models.Model):
    """Informations complémentaires liées à un compte utilisateur Django."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")
    photo = models.ImageField("Photo de profil", upload_to="profils/", blank=True, null=True)
    bio = models.TextField("Bio", max_length=300, blank=True)
    site_web = models.URLField("Site web", blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    def articles_publies(self):
        return self.user.articles.filter(statut=Article.Statut.PUBLIE)

    @property
    def nombre_suiveurs(self):
        return self.user.suivi_par.count()

    @property
    def nombre_suivis(self):
        return self.user.suit.count()

    @property
    def total_vues(self):
        return self.articles_publies().aggregate(total=models.Sum("vues"))["total"] or 0

    @property
    def total_likes(self):
        return sum(a.nombre_likes for a in self.articles_publies())


class Article(models.Model):
    class Statut(models.TextChoices):
        BROUILLON = "brouillon", "Brouillon"
        PUBLIE = "publie", "Publié"

    titre = models.CharField("Titre", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resume = models.CharField(
        "Résumé", max_length=300, blank=True,
        help_text="Affiché sur la liste des articles. Généré automatiquement si laissé vide.",
    )
    contenu = models.TextField("Contenu")
    image_couverture = models.ImageField(
        "Image de couverture", upload_to="couvertures/%Y/%m/", blank=True, null=True
    )
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    categorie = models.ForeignKey(
        Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.PUBLIE)

    vues = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="articles_aimes")

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_publication = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_publication"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unique(Article, self.titre, self.pk)
        if not self.resume:
            texte = " ".join(self.contenu.split())
            self.resume = (texte[:270] + "…") if len(texte) > 270 else texte
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("detail_article", kwargs={"slug": self.slug})

    @property
    def nombre_mots(self):
        return len(self.contenu.split())

    @property
    def temps_lecture(self):
        """Temps de lecture estimé, à ~200 mots/minute, arrondi au supérieur, minimum 1."""
        minutes = math.ceil(self.nombre_mots / 200)
        return max(minutes, 1)

    @property
    def nombre_likes(self):
        return self.likes.count()

    @property
    def est_brouillon(self):
        return self.statut == self.Statut.BROUILLON


class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="commentaires")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentaires")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="reponses"
    )
    contenu = models.TextField(max_length=1000)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_creation"]

    def __str__(self):
        return f"Commentaire de {self.auteur} sur « {self.article} »"

    @property
    def est_reponse(self):
        return self.parent_id is not None

    @property
    def nombre_signalements(self):
        return self.signalements.count()


class Suivi(models.Model):
    """Un utilisateur (suiveur) qui suit un autre utilisateur (auteur suivi)."""

    suiveur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suit")
    auteur_suivi = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suivi_par")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("suiveur", "auteur_suivi")
        verbose_name = "Suivi"
        verbose_name_plural = "Suivis"

    def __str__(self):
        return f"{self.suiveur} suit {self.auteur_suivi}"


REACTIONS_DISPONIBLES = [
    ("jaime", "👍"),
    ("jadore", "❤️"),
    ("rire", "😂"),
    ("wow", "😮"),
    ("triste", "😢"),
]


class ReactionCommentaire(models.Model):
    commentaire = models.ForeignKey(
        Commentaire, on_delete=models.CASCADE, related_name="reactions"
    )
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    emoji = models.CharField(max_length=10, choices=REACTIONS_DISPONIBLES)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("commentaire", "utilisateur", "emoji")

    def __str__(self):
        return f"{self.utilisateur} a réagi {self.emoji} sur un commentaire"


class SignalementCommentaire(models.Model):
    commentaire = models.ForeignKey(
        Commentaire, on_delete=models.CASCADE, related_name="signalements"
    )
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="signalements")
    raison = models.CharField(max_length=200, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("commentaire", "utilisateur")

    def __str__(self):
        return f"Signalement de {self.utilisateur} sur un commentaire"
