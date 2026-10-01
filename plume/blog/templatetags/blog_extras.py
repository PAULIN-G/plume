import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import slugify

register = template.Library()


CODE_BLOC_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
TITRE_RE = re.compile(r"^(#{2,3})\s+(.*)$", re.MULTILINE)


def _extraire_titre_ancres(texte_echappe):
    """Remplace les lignes '## Titre' par des <h2 id="..."> / <h3 id="..."> et
    renvoie (texte_modifie, liste_des_titres_pour_la_toc)."""
    titres = []

    def remplace(match):
        niveau = len(match.group(1))
        libelle = match.group(2).strip()
        ancre = slugify(libelle) or f"section-{len(titres) + 1}"
        # Garantit l'unicité de l'ancre si deux titres se ressemblent
        base_ancre, n = ancre, 1
        while any(t["ancre"] == ancre for t in titres):
            n += 1
            ancre = f"{base_ancre}-{n}"
        titres.append({"ancre": ancre, "texte": libelle, "niveau": niveau})
        balise = "h2" if niveau == 2 else "h3"
        return f'@@TITRE_{len(titres) - 1}@@'

    texte_modifie = TITRE_RE.sub(remplace, texte_echappe)
    return texte_modifie, titres


def _reinjecte_titres(html, titres):
    for i, t in enumerate(titres):
        balise = "h2" if t["niveau"] == 2 else "h3"
        html = html.replace(
            f"<p>@@TITRE_{i}@@</p>",
            f'<{balise} id="{t["ancre"]}">{t["texte"]}</{balise}>',
        )
    return html


def _extraire_blocs_code(texte_echappe):
    """Sort temporairement les blocs ```code``` du texte pour éviter que le
    reste du traitement (gras, italique, paragraphes) ne les abîme."""
    blocs = []

    def remplace(match):
        langage = match.group(1) or "texte"
        code = match.group(2)
        blocs.append((langage, code))
        return f"@@CODE_{len(blocs) - 1}@@"

    texte_modifie = CODE_BLOC_RE.sub(remplace, texte_echappe)
    return texte_modifie, blocs


def _reinjecte_blocs_code(html, blocs):
    for i, (langage, code) in enumerate(blocs):
        bloc_html = (
            f'<div class="bloc-code">'
            f'<button type="button" class="bouton-copier" data-copier>Copier</button>'
            f'<pre data-langage="{langage}"><code>{code}</code></pre>'
            f"</div>"
        )
        html = html.replace(f"<p>@@CODE_{i}@@</p>", bloc_html)
    return html


@register.filter(name="mise_en_forme")
def mise_en_forme(texte):
    """
    Convertit une syntaxe très simple façon Markdown en HTML :
    ## Titre / ### Sous-titre (avec ancre pour la table des matières),
    ```code``` en bloc de code, **gras**, *italique*,
    lignes commençant par "- " en liste à puces,
    et double saut de ligne en nouveau paragraphe.
    Le texte est d'abord échappé pour rester sûr (pas d'injection HTML).
    """
    if not texte:
        return ""

    texte = escape(texte)

    texte, blocs_code = _extraire_blocs_code(texte)
    texte, titres = _extraire_titre_ancres(texte)

    texte = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texte)
    texte = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<em>\1</em>", texte)

    blocs = texte.split("\n\n")
    html_blocs = []
    for bloc in blocs:
        lignes = [l for l in bloc.split("\n") if l.strip() != ""]
        if lignes and all(l.strip().startswith("- ") for l in lignes):
            items = "".join(f"<li>{l.strip()[2:]}</li>" for l in lignes)
            html_blocs.append(f"<ul>{items}</ul>")
        else:
            html_blocs.append(f"<p>{'<br>'.join(lignes)}</p>")

    html = "".join(html_blocs)
    html = _reinjecte_titres(html, titres)
    html = _reinjecte_blocs_code(html, blocs_code)

    return mark_safe(html)


@register.simple_tag
def table_des_matieres(texte):
    """Renvoie la liste des titres ## et ### présents dans le contenu, pour la TOC."""
    if not texte:
        return []
    texte_echappe = escape(texte)
    _, titres = _extraire_titre_ancres(texte_echappe)
    return titres


@register.filter(name="initiale")
def initiale(username):
    if not username:
        return "?"
    return username[0].upper()


@register.simple_tag
def reactions_groupees(commentaire, user):
    """
    Regroupe les réactions d'un commentaire par emoji : renvoie une liste de
    dicts {emoji, total, active} où 'active' indique si CET utilisateur a
    déjà réagi avec cet emoji (pour le mettre en surbrillance).
    """
    from collections import OrderedDict

    from ..models import REACTIONS_DISPONIBLES

    compteurs = OrderedDict((code, {"emoji": code, "total": 0, "active": False}) for code, _ in REACTIONS_DISPONIBLES)
    for reaction in commentaire.reactions.all():
        if reaction.emoji in compteurs:
            compteurs[reaction.emoji]["total"] += 1
            if user.is_authenticated and reaction.utilisateur_id == user.id:
                compteurs[reaction.emoji]["active"] = True

    emoji_affiche = {
        "jaime": "👍", "jadore": "❤️", "rire": "😂", "wow": "😮", "triste": "😢",
    }
    resultat = []
    for code, data in compteurs.items():
        resultat.append({**data, "symbole": emoji_affiche.get(code, "•")})
    return resultat


@register.simple_tag
def url_active(request, url_name, *args, **kwargs):
    """Retourne 'actif' si l'URL correspond à la page courante (utile pour la nav)."""
    from django.urls import resolve

    try:
        match = resolve(request.path)
        return "actif" if match.url_name == url_name else ""
    except Exception:
        return ""
