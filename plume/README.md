# 🪶 Plume — un blog moderne en Django

Blog complet avec authentification, articles, catégories, tags, likes,
commentaires imbriqués, profils utilisateurs, mode sombre, et prêt pour le
déploiement en production.

## ✨ Fonctionnalités

- Inscription / connexion / déconnexion / changement de mot de passe
- Création, modification, suppression d'articles (CRUD complet)
- Brouillons vs articles publiés
- Catégories (avec couleur) + tags
- Recherche full-text (titre + contenu)
- Pagination
- Upload d'image de couverture par article
- Profils utilisateurs publics (photo, bio, site web)
- Likes sur les articles
- Commentaires avec réponses imbriquées (1 niveau)
- Compteur de vues par article (une fois par session)
- Temps de lecture estimé automatique
- Articles similaires (même catégorie)
- Articles populaires + tags populaires en sidebar
- Mode sombre / clair (mémorisé dans le navigateur, respecte aussi la préférence système)
- Interface d'administration Django personnalisée
- Design responsive, moderne, sans dépendance JS lourde
- **Table des matières auto-générée** avec suivi de section active au scroll
- **Barre de progression de lecture** en haut de page
- **Blocs de code colorés** avec bouton "Copier" (syntaxe \`\`\`code\`\`\`)
- **Suivre un auteur** (abonnés / suivis, visibles sur chaque profil)
- **Réactions emoji** sur les commentaires (👍❤️😂😮😢)
- **Signalement de commentaires** (modération via l'admin)
- **Tableau de bord auteur** : vues, likes, commentaires et abonnés en un coup d'œil
- **SEO** : meta tags Open Graph (belles previews de partage), sitemap.xml, flux RSS, robots.txt

## ✍️ Syntaxe pour écrire un article

Le champ "Contenu" accepte une mise en forme légère, sans éditeur riche :

- `## Titre de section` / `### Sous-titre` → génèrent la table des matières
- `**gras**` / `*italique*`
- Lignes commençant par `- ` → liste à puces
- Un bloc entouré de triples apostrophes inversées (comme sur GitHub), avec
  le nom du langage juste après les premières, devient un bloc de code
  coloré avec un bouton "Copier".

## 📁 Structure du projet

```
plume/
├── manage.py
├── requirements.txt
├── .env.example          # à copier en .env
├── Procfile               # pour Render / Heroku
├── build.sh                # script de build (collectstatic + migrate)
├── render.yaml             # déploiement en un clic sur Render
├── config/                 # configuration du projet Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── blog/                    # l'application principale
    ├── models.py            # Article, Categorie, Tag, Commentaire, Profil
    ├── views.py
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── signals.py           # crée un Profil à chaque inscription
    ├── templatetags/        # filtre de mise en forme du texte
    ├── management/commands/seed_demo.py   # données de démo
    ├── templates/blog/
    └── static/blog/
```

## 🚀 Installation en local

### 1. Prérequis
- Python 3.11 ou plus récent
- pip

### 2. Cloner / dézipper le projet, puis se placer dedans

```bash
cd plume
```

### 3. Créer un environnement virtuel

```bash
python -m venv venv
```

Sur Windows :
```powershell
venv\Scripts\activate
```

Sur Mac/Linux :
```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configurer les variables d'environnement

```bash
cp .env.example .env
```

(Sur Windows, utilise `copy .env.example .env`)

Le fichier `.env` par défaut fonctionne tel quel pour un essai en local
(SQLite, DEBUG=True). Tu peux le laisser sans rien changer pour commencer.

### 6. Appliquer les migrations

```bash
python manage.py migrate
```

### 7. Créer un compte administrateur

```bash
python manage.py createsuperuser
```

### 8. (Optionnel) Charger des données de démonstration

Catégories, tags, un utilisateur `demo` (mot de passe `demo12345`) et
quelques articles d'exemple :

```bash
python manage.py seed_demo
```

### 9. Lancer le serveur

```bash
python manage.py runserver
```

Ouvre **http://127.0.0.1:8000** dans ton navigateur. 🎉

L'interface d'administration est sur **http://127.0.0.1:8000/admin/**

## 🌍 Déploiement en production (Render.com — gratuit)

[Render](https://render.com) propose un plan gratuit simple, avec base de
données PostgreSQL incluse. Le fichier `render.yaml` fourni permet un
déploiement quasi automatique.

### Option A — Déploiement via Blueprint (le plus simple)

1. Pousse ce projet sur un dépôt GitHub (public ou privé)
2. Va sur [render.com](https://render.com) → **New** → **Blueprint**
3. Connecte ton dépôt GitHub
4. Render détecte automatiquement `render.yaml` et propose de créer :
   - le service web (avec build automatique via `build.sh`)
   - une base de données PostgreSQL gratuite
5. Clique sur **Apply** — Render installe, migre, et démarre le site
6. Une fois déployé, ouvre le **Shell** du service dans le tableau de bord Render et lance :
   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo   # optionnel
   ```

### Option B — Déploiement manuel (sans Blueprint)

1. Crée un nouveau **Web Service** sur Render, connecté à ton dépôt
2. Renseigne :
   - **Build Command** : `./build.sh`
   - **Start Command** : `gunicorn config.wsgi:application`
3. Crée une base **PostgreSQL** (New → PostgreSQL), copie son "Internal Database URL"
4. Dans les variables d'environnement du Web Service, ajoute :
   - `SECRET_KEY` → génère-en une (voir `.env.example` pour la commande)
   - `DEBUG` → `False`
   - `ALLOWED_HOSTS` → `.onrender.com`
   - `DATABASE_URL` → l'URL PostgreSQL copiée à l'étape précédente
5. Déploie, puis crée ton compte admin via le Shell Render comme ci-dessus

### Autres hébergeurs

Le projet fonctionne aussi tel quel sur **Railway**, **Heroku**, ou tout
hébergeur supportant `Procfile` + variables d'environnement — le
fonctionnement est le même : `build.sh` (ou son équivalent) installe les
dépendances, collecte les fichiers statiques et migre la base ; `Procfile`
démarre l'application avec Gunicorn.

## 🔐 Sécurité avant la mise en production

- [ ] Change `SECRET_KEY` (ne garde jamais celle par défaut)
- [ ] Mets `DEBUG=False`
- [ ] Renseigne correctement `ALLOWED_HOSTS`
- [ ] Ne commite jamais ton fichier `.env` réel (déjà exclu par `.gitignore`)

## 🛠️ Commandes utiles

```bash
# Créer une migration après avoir modifié un modèle
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Ouvrir un shell Python avec le contexte Django chargé
python manage.py shell

# Collecter les fichiers statiques (nécessaire avant un déploiement)
python manage.py collectstatic
```

## 🧭 Aller plus loin (idées d'évolutions)

- API REST avec Django REST Framework
- Éditeur de texte riche (WYSIWYG) pour la rédaction
- Notifications par email (nouveau commentaire, nouvelle réponse)
- Tests automatisés (`pytest-django`)
- Système de brouillons avec aperçu avant publication

---

Fait avec Django, pensé pour être simple à comprendre et à faire évoluer.
