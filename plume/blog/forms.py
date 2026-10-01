from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Article, Commentaire, Profil, Tag


class ClasseFormMixin:
    """Ajoute automatiquement une classe CSS à tous les champs d'un formulaire."""

    css_class = "champ-form"

    def stylise_les_champs(self):
        for nom_champ, champ in self.fields.items():
            widget = champ.widget
            classes_existantes = widget.attrs.get("class", "")
            widget.attrs["class"] = (classes_existantes + " " + self.css_class).strip()
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs["class"] = "champ-checkbox"


class InscriptionForm(ClasseFormMixin, UserCreationForm):
    email = forms.EmailField(required=False, label="Adresse e-mail")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stylise_les_champs()


class ArticleForm(ClasseFormMixin, forms.ModelForm):
    tags_texte = forms.CharField(
        label="Tags",
        required=False,
        help_text="Sépare les tags par des virgules, ex : django, tutoriel, web",
    )

    class Meta:
        model = Article
        fields = [
            "titre", "categorie", "image_couverture", "resume", "contenu", "statut",
        ]
        widgets = {
            "contenu": forms.Textarea(attrs={"rows": 14, "placeholder": "Écris ton article ici… (le format Markdown simple est supporté : **gras**, *italique*, listes avec -)"}),
            "resume": forms.Textarea(attrs={"rows": 2, "placeholder": "Laisse vide pour générer un résumé automatique"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categorie"].required = False
        self.fields["categorie"].empty_label = "— Aucune catégorie —"
        if self.instance and self.instance.pk:
            self.fields["tags_texte"].initial = ", ".join(
                t.nom for t in self.instance.tags.all()
            )
        self.stylise_les_champs()

    def save(self, commit=True):
        article = super().save(commit=commit)
        if commit:
            self._sauver_tags(article)
        return article

    def _sauver_tags(self, article):
        noms = [n.strip() for n in self.cleaned_data.get("tags_texte", "").split(",") if n.strip()]
        tags = []
        for nom in noms:
            tag = Tag.objects.filter(nom__iexact=nom).first()
            if tag is None:
                tag = Tag.objects.create(nom=nom)
            tags.append(tag)
        article.tags.set(tags)


class CommentaireForm(ClasseFormMixin, forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ["contenu"]
        widgets = {
            "contenu": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Écris ton commentaire..."}
            ),
        }
        labels = {"contenu": ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stylise_les_champs()


class ProfilForm(ClasseFormMixin, forms.ModelForm):
    first_name = forms.CharField(label="Prénom", max_length=150, required=False)
    last_name = forms.CharField(label="Nom", max_length=150, required=False)

    class Meta:
        model = Profil
        fields = ["photo", "bio", "site_web"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Parle un peu de toi..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
        self.stylise_les_champs()

    def save(self, commit=True):
        profil = super().save(commit=commit)
        if commit:
            profil.user.first_name = self.cleaned_data.get("first_name", "")
            profil.user.last_name = self.cleaned_data.get("last_name", "")
            profil.user.save()
        return profil
