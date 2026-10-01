from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Article, Categorie, Commentaire, Tag


class Command(BaseCommand):
    help = "Remplit le blog avec des catégories, tags, un auteur de démo et quelques articles."

    def handle(self, *args, **options):
        auteur, cree = User.objects.get_or_create(
            username="demo", defaults={"email": "demo@example.com"}
        )
        if cree:
            auteur.set_password("demo12345")
            auteur.save()
            self.stdout.write(self.style.SUCCESS("Utilisateur 'demo' créé (mot de passe: demo12345)"))

        categories_data = [
            ("Technologie", "#6366f1", "Actualités, tutoriels et réflexions autour de la tech."),
            ("Voyage", "#f59e0b", "Carnets de route et conseils pour voyager mieux."),
            ("Cuisine", "#10b981", "Recettes et découvertes culinaires."),
            ("Vie perso", "#ec4899", "Réflexions, organisation, productivité."),
        ]
        categories = []
        for nom, couleur, description in categories_data:
            cat, _ = Categorie.objects.get_or_create(
                nom=nom, defaults={"couleur": couleur, "description": description}
            )
            categories.append(cat)

        tags_noms = ["django", "python", "astuce", "debutant", "productivite", "recette", "afrique"]
        tags = [Tag.objects.get_or_create(nom=n)[0] for n in tags_noms]

        articles_data = [
            {
                "titre": "Bien démarrer avec Django en 2026",
                "categorie": categories[0],
                "contenu": (
                    "## Pourquoi Django ?\n\n"
                    "Django reste l'un des frameworks web les plus fiables pour construire "
                    "rapidement des applications solides.\n\n"
                    "## Les trois briques de base\n\n"
                    "Dans cet article, on revient sur les bases : **modèles**, **vues**, "
                    "**templates**, et comment ils communiquent entre eux.\n\n"
                    "- Un modèle décrit tes données\n"
                    "- Une vue contient la logique\n"
                    "- Un template affiche le résultat\n\n"
                    "### Un exemple de modèle\n\n"
                    "```python\n"
                    "class Article(models.Model):\n"
                    "    titre = models.CharField(max_length=200)\n"
                    "    contenu = models.TextField()\n"
                    "```\n\n"
                    "Avec un peu de pratique, ces trois briques deviennent un réflexe naturel."
                ),
                "tags": ["django", "python", "debutant"],
            },
            {
                "titre": "5 astuces pour organiser ses journées de travail",
                "categorie": categories[3],
                "contenu": (
                    "La productivité, ce n'est pas *faire plus*, c'est *faire ce qui compte*.\n\n"
                    "- Bloque des plages dédiées à la concentration\n"
                    "- Traite tes emails à heures fixes\n"
                    "- Termine ta journée en préparant la suivante\n\n"
                    "Petit à petit, ces habitudes changent vraiment la donne."
                ),
                "tags": ["productivite", "astuce"],
            },
            {
                "titre": "Un carnet de route à Kribi",
                "categorie": categories[1],
                "contenu": (
                    "Kribi, entre plage et forêt, reste une destination sous-estimée.\n\n"
                    "Entre les chutes de la Lobé qui se jettent directement dans l'océan et "
                    "les villages de pêcheurs, il y a de quoi remplir plusieurs jours de "
                    "découvertes.\n\n"
                    "**Conseil pratique** : prévois de la crème solaire, le soleil y est franc "
                    "toute l'année."
                ),
                "tags": ["afrique"],
            },
            {
                "titre": "Ma recette rapide de riz sauté aux légumes",
                "categorie": categories[2],
                "contenu": (
                    "Une recette simple, rapide, et personnalisable selon ce que tu as sous la main.\n\n"
                    "- Riz cuit refroidi (idéalement de la veille)\n"
                    "- Légumes de saison en petits dés\n"
                    "- Un peu d'huile, d'ail et de sauce soja\n\n"
                    "Fais revenir les légumes à feu vif, ajoute le riz, mélange et sers chaud."
                ),
                "tags": ["recette"],
            },
        ]

        for data in articles_data:
            if Article.objects.filter(titre=data["titre"]).exists():
                continue
            article = Article.objects.create(
                titre=data["titre"],
                contenu=data["contenu"],
                auteur=auteur,
                categorie=data["categorie"],
                statut=Article.Statut.PUBLIE,
            )
            article.tags.set([t for t in tags if t.nom in data["tags"]])
            Commentaire.objects.create(
                article=article, auteur=auteur, contenu="Merci pour cet article, très clair !"
            )

        self.stdout.write(self.style.SUCCESS("Données de démonstration installées avec succès."))
