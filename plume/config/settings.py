```python
"""
Configuration Django pour le projet Plume.

Les valeurs sensibles sont lues depuis les variables d'environnement :
- fichier .env en local
- variables d'environnement en production
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# CONFIGURATION DE BASE
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Charge le fichier .env s'il existe
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# SÉCURITÉ
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-CHANGE-MOI-avant-le-deploiement-en-production",
)

# En production, DEBUG doit être False
DEBUG = env_bool("DEBUG", default=False)


# ---------------------------------------------------------------------------
# HÔTES AUTORISÉS
# ---------------------------------------------------------------------------

def _hosts_from_env(name, default=""):
    return [
        host.strip()
        for host in os.environ.get(name, default).split(",")
        if host.strip()
    ]


def _ajouter_hote(liste, hote):
    if hote and hote not in liste:
        liste.append(hote)


ALLOWED_HOSTS = _hosts_from_env("ALLOWED_HOSTS", "localhost,127.0.0.1")

# Prévisualisations et production Vercel : *.vercel.app
# (chaque déploiement a un sous-domaine différent, d'où le joker)
_ajouter_hote(ALLOWED_HOSTS, ".vercel.app")

# Variables injectées automatiquement par Vercel (sans https://)
for var in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL", "VERCEL_BRANCH_URL"):
    valeur = os.environ.get(var, "").strip()
    if valeur.startswith("http://") or valeur.startswith("https://"):
        valeur = valeur.split("://", 1)[1]
    _ajouter_hote(ALLOWED_HOSTS, valeur.rstrip("/"))

# Compatibilité Render
_ajouter_hote(ALLOWED_HOSTS, os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip())

# Derrière le proxy Vercel, l'hôte réel arrive dans X-Forwarded-Host
if os.environ.get("VERCEL"):
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = _hosts_from_env("CSRF_TRUSTED_ORIGINS")


def _ajouter_origine(origine):
    if origine and origine not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origine)


_ajouter_origine("https://*.vercel.app")

for var in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL", "VERCEL_BRANCH_URL"):
    valeur = os.environ.get(var, "").strip()
    if not valeur:
        continue
    if valeur.startswith("http://") or valeur.startswith("https://"):
        _ajouter_origine(valeur.rstrip("/"))
    else:
        _ajouter_origine(f"https://{valeur.rstrip('/')}")

if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    _ajouter_origine(f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}")


# ---------------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "blog",
]

SITE_ID = 1


# ---------------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------------------------
# URL / TEMPLATES
# ---------------------------------------------------------------------------

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blog.context_processors.parametres_globaux",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# BASE DE DONNÉES
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Production : PostgreSQL ou autre base fournie par l'hébergeur
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }

else:
    # Développement local : SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------------------------------------------------------------------------
# VALIDATION DES MOTS DE PASSE
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


# ---------------------------------------------------------------------------
# INTERNATIONALISATION
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# FICHIERS STATIQUES
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ---------------------------------------------------------------------------
# FICHIERS MÉDIA
# ---------------------------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# CONFIGURATION GÉNÉRALE
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# AUTHENTIFICATION
# ---------------------------------------------------------------------------

LOGIN_URL = "connexion"

LOGIN_REDIRECT_URL = "liste_articles"

LOGOUT_REDIRECT_URL = "liste_articles"


# ---------------------------------------------------------------------------
# EMAILS
# ---------------------------------------------------------------------------

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)


# ---------------------------------------------------------------------------
# SÉCURITÉ EN PRODUCTION
# ---------------------------------------------------------------------------

if not DEBUG:

    SECURE_SSL_REDIRECT = env_bool(
        "SECURE_SSL_REDIRECT",
        default=True,
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )
