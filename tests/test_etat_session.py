from datetime import date
from types import SimpleNamespace

import pytest

import etat_session
from modeles import UserProfile


@pytest.fixture
def session_simulee(monkeypatch):
    profil = UserProfile().demarrer_parcours(
        "conception",
        date.today(),
    )

    session = {
        "profil": profil,
        "suivi_conception": {"dernieres_regles": date.today()},
        "suivi_grossesse": None,
        "confirmer_import": True,
    }

    monkeypatch.setattr(
        etat_session,
        "st",
        SimpleNamespace(session_state=session),
    )

    return session


@pytest.mark.parametrize("signal", [None, False, "true"])
def test_effacement_global_sans_succes_preserve_session(
    session_simulee,
    signal,
):
    session_simulee["stockage_profil"] = {"effacement": signal}
    avant = session_simulee.copy()

    etat_session.finaliser_effacement_global()

    assert session_simulee == avant


def test_effacement_global_apres_succes_reinitialise_session(
    session_simulee,
):
    ancien_identifiant = session_simulee["profil"].id
    session_simulee["stockage_profil"] = {"effacement": True}

    etat_session.finaliser_effacement_global()

    profil = session_simulee["profil"]

    assert profil.id != ancien_identifiant
    assert profil.journeys == ()
    assert profil.active_journey_id is None
    assert session_simulee["suivi_conception"] is None
    assert session_simulee["suivi_grossesse"] is None
    assert "confirmer_import" not in session_simulee
    assert "stockage_profil" not in session_simulee
    assert session_simulee["message_effacement"] == (
        "La sauvegarde locale et les données de session ont été effacées."
    )

    # Un second appel sans nouveau signal ne doit rien changer.
    apres = session_simulee.copy()

    etat_session.finaliser_effacement_global()

    assert session_simulee == apres

def test_remplacement_profil_efface_session_assistant(session_simulee):
    session_simulee.update({
        "assistant_question": "Question personnelle fictive",
        "assistant_apercu": {"question": "Question fictive"},
        "assistant_autorisation": True,
        "assistant_resultat": {"reponse": "Réponse fictive"},
        "preference_temoin": "à conserver",
        "preparation_rdv_notes_fictive": True,
        "preparation_rdv_apercu_fictive": {"messages": []},
    })
    nouveau_profil = UserProfile()

    etat_session.remplacer_profil_session(nouveau_profil)

    assert session_simulee["profil"] == nouveau_profil
    assert not any(
        cle.startswith(("assistant_", "preparation_rdv_"))
        for cle in session_simulee
    )
    assert session_simulee["preference_temoin"] == "à conserver"