from django.contrib.sitemaps import Sitemap

from .models import Article, Categorie


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(statut=Article.Statut.PUBLIE)

    def lastmod(self, obj):
        return obj.date_modification

    def location(self, obj):
        return obj.get_absolute_url()


class CategorieSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Categorie.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()
