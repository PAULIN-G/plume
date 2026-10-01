from .models import Categorie


def parametres_globaux(request):
    """Rend certaines données disponibles dans TOUS les templates (ex: nav des catégories)."""
    return {
        "toutes_categories": Categorie.objects.all(),
        "nom_site": "Plume",
    }
