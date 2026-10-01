#!/usr/bin/env bash
# Script exécuté par Render (ou tout hébergeur compatible) avant chaque déploiement.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
