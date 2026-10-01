from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Article


class DerniersArticlesFeed(Feed):
    title = "Plume — derniers articles"
    link = "/"
    description = "Les articles les plus récents publiés sur Plume."

    def items(self):
        return Article.objects.filter(statut=Article.Statut.PUBLIE)[:20]

    def item_title(self, item):
        return item.titre

    def item_description(self, item):
        return item.resume

    def item_link(self, item):
        return reverse("detail_article", kwargs={"slug": item.slug})

    def item_author_name(self, item):
        return item.auteur.username

    def item_pubdate(self, item):
        return item.date_publication
