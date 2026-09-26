import streamlit as st

_composant_stockage = st.components.v2.component( # type: ignore
    "nurtureai_essai_stockage",
    html="""
        <button id="enregistrer_exemple" type="button">
            Enregistrer le profil dans ce navigateur
        </button>
        <button id="effacer" type="button">
            Effacer la sauvegarde locale
        </button>
        <p id="message" role="status"></p>
    """,
    js="""
        export default function({ parentElement, setStateValue, data }) {
            const cle = data.cle_stockage;
            const effacer = parentElement.querySelector("#effacer");
            const message = parentElement.querySelector("#message");
            const enregistrerExemple = parentElement.querySelector("#enregistrer_exemple");

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

            enregistrerExemple.onclick = () => {
                try {
                    const texte = data.json_exemple;

                    localStorage.setItem(cle, texte);
                    setStateValue("texte", texte);
                    setStateValue("erreur_operation", null);
                    message.textContent = "Profil enregistré dans ce navigateur.";
                } catch (erreur) {
                    message.textContent = "Enregistrement du profil impossible.";
                    setStateValue(
                        "erreur_operation",
                        "Le profil proposé n’a pas pu être enregistré."
                    );
                }
            };

            effacer.onclick = () => {
                try {
                    localStorage.removeItem(cle);
                    setStateValue("texte", "");
                    setStateValue("erreur_operation", null);
                    message.textContent = "Sauvegarde locale effacée.";
                } catch (erreur) {
                    message.textContent = "Effacement impossible.";
                    setStateValue(
                        "erreur_operation",
                        "L’effacement a échoué. Les données peuvent encore être présentes."
                    );
                }
            };

            return () => {
                enregistrerExemple.onclick = null;
                effacer.onclick = null;
            };
        }
    """,
)

def afficher_stockage_navigateur(
    json_propose: str,
    *,
    cle_stockage: str,
    key: str,
):
    """Affiche le composant et retourne les données reçues du navigateur."""
    etat_composant = st.session_state.get(key, {})
    lecture = etat_composant.get("lecture")

    return _composant_stockage(
        key=key,
        data={
            "demander_lecture": lecture is None,
            "json_exemple": json_propose,
            "cle_stockage": cle_stockage,
        },
        on_texte_change=lambda: None,
        on_lecture_change=lambda: None,
        on_erreur_operation_change=lambda: None,
    )

