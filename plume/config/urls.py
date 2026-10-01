from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from blog import views as blog_views
from blog.feeds import DerniersArticlesFeed
from blog.sitemaps import ArticleSitemap, CategorieSitemap

sitemaps = {
    "articles": ArticleSitemap,
    "categories": CategorieSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("rss/", DerniersArticlesFeed(), name="rss_feed"),
    path("robots.txt", blog_views.robots_txt, name="robots_txt"),
    path("", include("blog.urls")),
]

# Sert les fichiers uploadés (images) en développement.
# En production, un vrai service de stockage ou le serveur web s'en charge,
# mais ça ne pose aucun problème de le laisser actif ici aussi pour un petit projet.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
