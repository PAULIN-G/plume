// --- Bascule thème clair / sombre, sauvegardée dans localStorage ------------
(function () {
    const bouton = document.getElementById("toggle-theme");
    if (!bouton) return;

    bouton.addEventListener("click", function () {
        const actuel = document.documentElement.getAttribute("data-theme") || "clair";
        const nouveau = actuel === "clair" ? "sombre" : "clair";
        document.documentElement.setAttribute("data-theme", nouveau);
        localStorage.setItem("plume-theme", nouveau);
    });
})();

// --- Menu utilisateur : clic (nécessaire sur tactile, le survol ne suffit pas)
(function () {
    const menus = document.querySelectorAll(".menu-utilisateur");
    if (!menus.length) return;

    menus.forEach(function (menu) {
        const bouton = menu.querySelector(".avatar-btn");
        if (!bouton) return;
        bouton.addEventListener("click", function (e) {
            e.stopPropagation();
            const ouvert = menu.classList.toggle("ouvert");
            bouton.setAttribute("aria-expanded", ouvert ? "true" : "false");
            menus.forEach(function (autre) {
                if (autre !== menu) {
                    autre.classList.remove("ouvert");
                    const b = autre.querySelector(".avatar-btn");
                    if (b) b.setAttribute("aria-expanded", "false");
                }
            });
        });
    });

    document.addEventListener("click", function () {
        menus.forEach(function (menu) {
            menu.classList.remove("ouvert");
            const b = menu.querySelector(".avatar-btn");
            if (b) b.setAttribute("aria-expanded", "false");
        });
    });
})();

document.querySelectorAll(".fermer-message").forEach(function (bouton) {
    bouton.addEventListener("click", function () {
        const message = bouton.closest(".message");
        if (message) message.remove();
    });
});

// --- Répondre à un commentaire : pré-remplit le champ caché parent_id -------
(function () {
    const form = document.getElementById("form-commentaire");
    if (!form) return;

    const champParentId = document.getElementById("parent_id");
    const zoneReponse = document.getElementById("reponse-a");
    const nomReponse = document.getElementById("reponse-a-nom");
    const boutonAnnuler = document.getElementById("annuler-reponse");
    const textarea = form.querySelector("textarea");

    document.querySelectorAll(".lien-repondre").forEach(function (bouton) {
        bouton.addEventListener("click", function () {
            const parentId = bouton.dataset.parentId;
            const auteur = bouton.dataset.auteur;
            champParentId.value = parentId;
            nomReponse.textContent = auteur;
            zoneReponse.hidden = false;
            if (textarea) {
                textarea.focus();
                textarea.placeholder = "Écris ta réponse à " + auteur + "...";
            }
            form.scrollIntoView({ behavior: "smooth", block: "center" });
        });
    });

    if (boutonAnnuler) {
        boutonAnnuler.addEventListener("click", function () {
            champParentId.value = "";
            zoneReponse.hidden = true;
            if (textarea) textarea.placeholder = "Écris ton commentaire...";
        });
    }
})();

// --- Barre de progression de lecture ----------------------------------------
(function () {
    const barre = document.getElementById("barre-progression");
    const article = document.getElementById("contenu-article");
    if (!barre || !article) return;

    function majBarre() {
        const rect = article.getBoundingClientRect();
        const hauteurTotale = rect.height - window.innerHeight;
        const lu = Math.min(Math.max(-rect.top, 0), Math.max(hauteurTotale, 1));
        const pourcentage = hauteurTotale > 0 ? (lu / hauteurTotale) * 100 : 0;
        barre.style.width = pourcentage + "%";
    }

    document.addEventListener("scroll", majBarre, { passive: true });
    window.addEventListener("resize", majBarre);
    majBarre();
})();

// --- Table des matières : suivi de la section active au scroll --------------
(function () {
    const liens = document.querySelectorAll("#liste-toc a");
    if (!liens.length) return;

    const cibles = Array.from(liens)
        .map(function (lien) {
            const id = lien.getAttribute("href").slice(1);
            return { lien: lien, section: document.getElementById(id) };
        })
        .filter(function (item) { return item.section; });

    function majActif() {
        let actif = null;
        const seuil = window.innerHeight * 0.3;
        cibles.forEach(function (item) {
            const rect = item.section.getBoundingClientRect();
            if (rect.top <= seuil) actif = item;
        });
        cibles.forEach(function (item) { item.lien.classList.remove("toc-actif"); });
        if (actif) actif.lien.classList.add("toc-actif");
    }

    document.addEventListener("scroll", majActif, { passive: true });
    majActif();

    liens.forEach(function (lien) {
        lien.addEventListener("click", function (e) {
            e.preventDefault();
            const id = lien.getAttribute("href").slice(1);
            const cible = document.getElementById(id);
            if (cible) {
                cible.scrollIntoView({ behavior: "smooth", block: "start" });
                history.pushState(null, "", "#" + id);
            }
        });
    });
})();

// --- Bouton "Copier" sur les blocs de code -----------------------------------
(function () {
    document.querySelectorAll("[data-copier]").forEach(function (bouton) {
        bouton.addEventListener("click", function () {
            const bloc = bouton.closest(".bloc-code");
            const code = bloc.querySelector("code");
            if (!code) return;
            navigator.clipboard.writeText(code.textContent).then(function () {
                const texteInitial = bouton.textContent;
                bouton.textContent = "Copié !";
                setTimeout(function () { bouton.textContent = texteInitial; }, 1500);
            });
        });
    });
})();
