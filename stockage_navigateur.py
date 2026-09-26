import streamlit as st

from collections.abc import Callable

_composant_stockage = st.components.v2.component( # type: ignore
    "nurtureai_essai_stockage",
    html="""
        <button id="enregistrer_exemple" type="button">
            Enregistrer le profil dans ce navigateur
        </button>
        <div>
            <label for="confirmer_effacement">
                <input id="confirmer_effacement" type="checkbox" />
                Je confirme vouloir supprimer la sauvegarde locale et toutes les données de session.
            </label>
        </div>
        <button id="effacer" type="button" disabled>
            Effacer la sauvegarde et la session
        </button>
        <p id="message" role="status"></p>
    """,
    js="""
        export default function({ parentElement, setStateValue, setTriggerValue, data }) {
            const cle = data.cle_stockage;
            const effacer = parentElement.querySelector("#effacer");
            const message = parentElement.querySelector("#message");
            const enregistrerExemple = parentElement.querySelector("#enregistrer_exemple");
            const confirmation = parentElement.querySelector("#confirmer_effacement");

            let texteReference = data.texte_reference;

            function verifierVersionLocale() {
                let erreur = null;

                if (!data.lecture_reussie || typeof texteReference !== "string") {
                    erreur = "Une lecture réussie du stockage est nécessaire avant cette action.";
                } else {
                    const texteActuel = localStorage.getItem(cle) ?? "";

                    if (texteActuel !== texteReference) {
                        erreur = (
                            "La sauvegarde a changé depuis sa lecture, par exemple dans un autre onglet. " +
                            "Exportez vos modifications de session si nécessaire, puis rechargez la page avant de réessayer."
                        );
                    }
                }

                if (erreur !== null) {
                    confirmation.checked = false;
                    effacer.disabled = true;
                    message.textContent = erreur;
                    setStateValue("erreur_operation", erreur);
                    return false;
                }

                return true;
            }

            async function modifierSousVerrou(action) {
                if (!navigator.locks?.request) {
                    const erreur = (
                        "La protection entre onglets est indisponible. Aucune modification du stockage n’a été effectuée. Vous pouvez exporter votre profil en JSON."
                    );
                    message.textContent = erreur;
                    setStateValue("erreur_operation", erreur);
                    return;
                }

                await navigator.locks.request(
                    "nurtureai:verrou:" + cle,
                    { ifAvailable: true },
                    (verrou) => {
                        if (!verrou) {
                            const erreur = (
                                "Une autre opération utilise la sauvegarde. Réessayez dans un instant."
                            );
                            message.textContent = erreur;
                            setStateValue("erreur_operation", erreur);
                            return;
                        }

                        if (!verifierVersionLocale()) {
                            return;
                        }

                        action();
                    }
                );
            }

            confirmation.checked = false;
            effacer.disabled = true;
            confirmation.onchange = () => {
                effacer.disabled = !confirmation.checked;
            };

            if (data.demander_lecture) {
                try {
                    const texte = localStorage.getItem(cle) ?? "";
                    setStateValue("texte", texte);
                    setStateValue("lecture", "ok");
                } catch (erreur) {
                    message.textContent = "Lecture du stockage impossible.";
                    setStateValue("lecture", "erreur");
                }
            }

            async function enregistrerProfil() {
                try {
                    await modifierSousVerrou(() => {
                        const texte = data.json_exemple;

                        localStorage.setItem(cle, texte);
                        texteReference = texte;

                        setStateValue("texte", texte);
                        setStateValue("erreur_operation", null);
                        message.textContent = "Profil enregistré dans ce navigateur.";
                    });
                } catch (erreur) {
                    message.textContent = "Enregistrement du profil impossible.";
                    setStateValue(
                        "erreur_operation",
                        "Le profil proposé n’a pas pu être enregistré."
                    );
                }
            }
            enregistrerExemple.onclick = enregistrerProfil;

            effacer.onclick = async () => {
                if (!confirmation.checked) {
                    return;
                }

                try {
                    await modifierSousVerrou(() => {
                        localStorage.removeItem(cle);
                        texteReference = "";

                        confirmation.checked = false;
                        effacer.disabled = true;

                        setStateValue("texte", "");
                        setStateValue("erreur_operation", null);
                        message.textContent = "Sauvegarde locale effacée.";
                        setTriggerValue("effacement", true);
                    });
                } catch (erreur) {
                    message.textContent = "Effacement impossible.";
                    setStateValue(
                        "erreur_operation",
                        "L’effacement a échoué. Les données peuvent encore être présentes."
                    );
                }
            };

            if (data.sauvegarde_auto) {
                void enregistrerProfil();
            }

            return () => {
                enregistrerExemple.onclick = null;
                effacer.onclick = null;
                confirmation.onchange = null;
            };
        }
    """,
)

def afficher_stockage_navigateur(
    json_propose: str,
    *,
    cle_stockage: str,
    key: str,
    on_effacement: Callable[[], None],
    sauvegarde_auto: bool = False,
):
    """Affiche le composant et retourne les données du navigateur."""
    reference_initiale = st.session_state.get(
        "lecture_initiale_stockage",
        {},
    )
    etat_composant = st.session_state.get(
        key,
        reference_initiale,
    )
    lecture = etat_composant.get("lecture")

    return _composant_stockage(
        key=key,
        default={
            "lecture": reference_initiale.get("lecture"),
            "texte": reference_initiale.get("texte"),
            "erreur_operation": None,
        },
        data={
            "demander_lecture": lecture is None,
            "lecture_reussie": lecture == "ok",
            "texte_reference": etat_composant.get("texte"),
            "json_exemple": json_propose,
            "cle_stockage": cle_stockage,
            "sauvegarde_auto": sauvegarde_auto,
        },
        on_texte_change=lambda: None,
        on_lecture_change=lambda: None,
        on_erreur_operation_change=lambda: None,
        on_effacement_change=on_effacement,
    )

_composant_lecture_initiale = st.components.v2.component( # type: ignore
    "nurtureai_lecture_initiale",
    js="""
        export default function({ data, setStateValue }) {
            if (!data.demander_lecture) {
                return;
            }

            try {
                const texte = localStorage.getItem(data.cle_stockage) ?? "";
                setStateValue("resultat", {
                    lecture: "ok",
                    texte: texte
                });
            } catch (erreur) {
                setStateValue("resultat", {
                    lecture: "erreur",
                    texte: null
                });
            }
        }
    """,
)


def lire_sauvegarde_initiale():
    key = "lecture_initiale_profil"
    etat = st.session_state.get(key, {})

    resultat = _composant_lecture_initiale(
        key=key,
        height=0,
        data={
            "cle_stockage": "nurtureai:profil:v1",
            "demander_lecture": etat.get("resultat") is None,
        },
        on_resultat_change=lambda: None,
    )

    return resultat.get("resultat")

