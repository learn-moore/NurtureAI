import pytest
from streamlit.testing.v1 import AppTest

import interface_assistant
from intentions import MESSAGE_URGENCE


def page_assistant():
    import streamlit as st
    from interface_assistant import afficher_assistant

    afficher_assistant()
    st.text("Suite de la page accessible.")


@pytest.mark.parametrize(
    "question, message_attendu",
    [
        ("   ", "Saisissez une question pour préparer l’aperçu."),
        ("C’est une urgence médicale pour moi.", MESSAGE_URGENCE),
    ],
)
def test_saisie_bloquee_avant_recherche(
    monkeypatch,
    question,
    message_attendu,
):
    def chargement_interdit(*args, **kwargs):
        pytest.fail("Le corpus ne devait pas être chargé.")

    monkeypatch.setattr(
        interface_assistant,
        "charger_corpus",
        chargement_interdit,
    )

    app = AppTest.from_function(page_assistant).run()

    assert not app.exception
    assert not app.json

    app.text_area(key="assistant_question").set_value(question)
    app.button[0].click().run()

    assert not app.exception
    assert message_attendu in [
        element.value for element in app.warning
    ]
    assert not app.json
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

def test_apercu_local_sans_profil_ni_appel_distant(monkeypatch):
    import json
    from datetime import date

    import assistant_groq
    from messages_assistant import CONSIGNES_MEDICALES
    from modeles import UserProfile

    def appel_interdit(*args, **kwargs):
        pytest.fail("L’aperçu ne doit pas appeler Groq.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 1, 1),
    )
    question = "À quoi sert une consultation avant une grossesse ?"

    app = AppTest.from_function(page_assistant).run()
    app.session_state["profil"] = profil

    app.text_area(key="assistant_question").set_value(question)
    app.button[0].click().run()

    assert not app.exception
    assert len(app.json) == 1

    messages = json.loads(app.json[0].value)
    assert len(messages) == 2
    assert messages[0] == {
        "role": "system",
        "content": CONSIGNES_MEDICALES,
    }
    assert messages[1]["role"] == "user"

    donnees = json.loads(messages[1]["content"])
    assert set(donnees) == {"question", "documents"}
    assert donnees["question"] == question

    identifiants = {
        document["id"]
        for document in donnees["documents"]
    }
    assert "conception_consultation_objectif" in identifiants

    assert profil.journeys[0].id not in app.json[0].value
    assert app.session_state["profil"] == profil
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

def test_corpus_invalide_affiche_message_controle(monkeypatch):
    def charger_invalide(*args, **kwargs):
        raise ValueError("Détail technique réservé au test.")

    monkeypatch.setattr(
        interface_assistant,
        "charger_corpus",
        charger_invalide,
    )

    app = AppTest.from_function(page_assistant).run()
    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button[0].click().run()

    assert not app.exception
    assert [element.value for element in app.error] == [
        "L’aperçu documentaire ne peut pas être préparé."
    ]
    assert not app.json
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]


def test_corpus_vide_ne_prepare_aucun_message(monkeypatch):
    monkeypatch.setattr(
        interface_assistant,
        "charger_corpus",
        lambda chemin: (),
    )

    app = AppTest.from_function(page_assistant).run()
    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button[0].click().run()

    assert not app.exception
    assert not app.json
    assert (
        "Aucun contexte documentaire ne peut être préparé pour cette question."
    ) in [element.value for element in app.info]
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

def test_apercu_conserve_sans_nouvelle_recherche(monkeypatch):
    app = AppTest.from_function(page_assistant).run()
    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert len(app.json) == 1
    apercu_initial = app.json[0].value

    def chargement_interdit(*args, **kwargs):
        pytest.fail("Le corpus ne devait pas être rechargé.")

    monkeypatch.setattr(
        interface_assistant,
        "charger_corpus",
        chargement_interdit,
    )

    app.run()

    assert not app.exception
    assert len(app.json) == 1
    assert app.json[0].value == apercu_initial

@pytest.mark.parametrize(
    "nouvelle_question",
    [
        "",
        "Quels sujets préparer avant une grossesse ?",
        "C’est une urgence médicale pour moi.",
    ],
)
def test_modifier_question_efface_apercu(
    monkeypatch,
    nouvelle_question,
):
    app = AppTest.from_function(page_assistant).run()
    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert len(app.json) == 1

    def chargement_interdit(*args, **kwargs):
        pytest.fail("Modifier la question ne doit pas lancer la recherche.")

    monkeypatch.setattr(
        interface_assistant,
        "charger_corpus",
        chargement_interdit,
    )

    app.text_area(key="assistant_question").set_value(
        nouvelle_question
    ).run()

    assert not app.exception
    assert not app.json
    assert "assistant_apercu" not in app.session_state
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

@pytest.mark.parametrize("modifier_question", [False, True])
def test_nouvel_apercu_retire_autorisation(
    monkeypatch,
    modifier_question,
):
    import assistant_groq

    def appel_interdit(*args, **kwargs):
        pytest.fail("Aucun appel distant ne doit être effectué.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    app = AppTest.from_function(page_assistant).run()
    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert not app.checkbox(key="assistant_autorisation").value
    apercu_initial = app.json[0].value

    app.checkbox(key="assistant_autorisation").check().run()

    assert not app.exception
    assert app.checkbox(key="assistant_autorisation").value
    assert app.json[0].value == apercu_initial

    if modifier_question:
        app.text_area(key="assistant_question").set_value(
            "Quels sujets préparer pour une consultation avant une grossesse ?"
        ).run()

        assert not app.exception
        assert not app.json

    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert len(app.json) == 1
    assert not app.checkbox(key="assistant_autorisation").value

@pytest.fixture
def apercu_assistant():
    question = "À quoi sert une consultation avant une grossesse ?"
    corpus = interface_assistant.charger_corpus(
        interface_assistant.CHEMIN_CORPUS
    )
    resultats = interface_assistant.rechercher_corpus(question, corpus)

    return {
        "question": question,
        "corpus": corpus,
        "messages": interface_assistant.preparer_messages(
            question,
            resultats,
            mode="medical",
        ),
        "consignes_classification": (
            interface_assistant.CONSIGNES_CLASSIFICATION
        ),
        "modele": interface_assistant.MODELE,
    }

def test_execution_transmet_apercu_exact(
    monkeypatch,
    apercu_assistant,
):
    import json
    import assistant_groq

    appels = []

    def faux_appel(messages, *, cle_api, modele):
        assert cle_api == "cle-fictive"
        assert modele == apercu_assistant["modele"]
        appels.append(messages)

        if len(appels) == 1:
            assert messages[0]["content"] == (
                apercu_assistant["consignes_classification"]
            )
            assert json.loads(messages[1]["content"]) == {
                "question": apercu_assistant["question"],
            }
            return "GENERAL_INFORMATION"

        assert len(appels) == 2
        assert messages == apercu_assistant["messages"]

        return json.dumps({
            "type": "reponse",
            "texte": (
                "Échanger sur le projet de grossesse "
                "[conception_consultation_objectif]."
            ),
        })

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    resultat = interface_assistant.executer_apercu_assistant(
        apercu_assistant,
        cle_api="cle-fictive",
    )

    assert len(appels) == 2
    assert resultat["statut"] == "references_controlees"

@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("messages", ()),
        ("consignes_classification", "Anciennes consignes fictives"),
        ("modele", "ancien-modele-fictif"),
    ],
)
def test_apercu_incompatible_bloque_envoi(
    monkeypatch,
    apercu_assistant,
    champ,
    valeur,
):
    import assistant_groq

    def appel_interdit(*args, **kwargs):
        pytest.fail("Un aperçu incompatible ne doit pas être envoyé.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )
    apercu_assistant[champ] = valeur

    with pytest.raises(ValueError, match="configuration courante"):
        interface_assistant.executer_apercu_assistant(
            apercu_assistant,
            cle_api="cle-fictive",
        )

def test_envoi_autorise_sans_relance_automatique(monkeypatch):
    import json
    import assistant_groq

    appels = []
    reponse = (
        "Échanger sur le projet de grossesse "
        "[conception_consultation_objectif]."
    )

    def faux_appel(messages, *, cle_api, modele):
        assert cle_api == "cle-fictive"
        assert modele == interface_assistant.MODELE
        appels.append(messages)

        if len(appels) == 1:
            return "GENERAL_INFORMATION"

        assert len(appels) == 2
        return json.dumps({
            "type": "reponse",
            "texte": reponse,
        })

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    app = AppTest.from_function(page_assistant)
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    assert not app.exception
    assert appels == []

    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert appels == []
    assert app.button(key="assistant_envoyer").disabled
    apercu = json.loads(app.json[0].value)

    app.checkbox(key="assistant_autorisation").check().run()

    assert not app.exception
    assert appels == []
    assert not app.button(key="assistant_envoyer").disabled

    app.button(key="assistant_envoyer").click().run()

    assert not app.exception
    assert len(appels) == 2
    assert list(appels[1]) == apercu
    assert reponse in [
        element.value for element in app.markdown
    ]
    assert "https://www.has-sante.fr/jcms/c_1360649/" in [
        element.value for element in app.text
    ]

    app.run()

    assert not app.exception
    assert len(appels) == 2
    assert reponse in [
        element.value for element in app.markdown
    ]

    app.text_area(key="assistant_question").set_value(
        "Quels sujets préparer avant une grossesse ?"
    ).run()

    assert not app.exception
    assert len(appels) == 2
    assert not app.json
    assert "assistant_resultat" not in app.session_state
    assert reponse not in [
        element.value for element in app.markdown
    ]

@pytest.mark.parametrize(
    "cas, statut_attendu, nombre_appels",
    [
        ("personnel", "generation_non_autorisee", 1),
        ("panne", "generation_indisponible", 2),
    ],
)
def test_refus_et_panne_preservent_la_page(
    monkeypatch,
    cas,
    statut_attendu,
    nombre_appels,
):
    import assistant_groq
    from assistant_documentaire import GenerationIndisponible
    from intentions import MESSAGE_SITUATION_PERSONNELLE

    appels = []

    def faux_appel(messages, *, cle_api, modele):
        assert cle_api == "cle-fictive"
        appels.append(messages)

        if len(appels) == 1:
            if cas == "personnel":
                return "PERSONAL_MEDICAL_SITUATION"
            return "GENERAL_INFORMATION"

        assert cas == "panne"
        assert len(appels) == 2
        raise GenerationIndisponible(
            "DETAIL_TECHNIQUE_FICTIF_NON_PUBLIC"
        )

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    app = AppTest.from_function(page_assistant)
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()
    app.checkbox(key="assistant_autorisation").check().run()
    app.button(key="assistant_envoyer").click().run()

    assert not app.exception
    assert len(appels) == nombre_appels
    assert f"Statut : {statut_attendu}" in [
        element.value for element in app.caption
    ]

    textes = [element.value for element in app.markdown]

    if cas == "personnel":
        assert MESSAGE_SITUATION_PERSONNELLE in textes
    else:
        assert (
            "La réponse documentaire est temporairement indisponible. Vous pouvez réessayer plus tard."
        ) in textes

    assert not app.session_state["assistant_resultat"]["sources"]
    assert "DETAIL_TECHNIQUE_FICTIF_NON_PUBLIC" not in "\n".join(textes)
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

@pytest.mark.parametrize("cle_invalide", ["", "   ", 42])
def test_configuration_invalide_bloque_envoi(
    monkeypatch,
    cle_invalide,
):
    import assistant_groq

    def appel_interdit(*args, **kwargs):
        pytest.fail("Une configuration invalide doit bloquer l’appel.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    app = AppTest.from_function(page_assistant)
    app.secrets["GROQ_API_KEY"] = cle_invalide
    app.run()

    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()
    app.checkbox(key="assistant_autorisation").check().run()

    app.session_state["assistant_resultat"] = {
        "statut": "references_controlees",
        "reponse": "ANCIENNE_REPONSE_FICTIVE",
        "sources": (),
    }

    app.button(key="assistant_envoyer").click().run()

    assert not app.exception
    assert "La configuration du service IA est invalide." in [
        element.value for element in app.error
    ]
    assert "assistant_resultat" not in app.session_state
    assert "ANCIENNE_REPONSE_FICTIVE" not in [
        element.value for element in app.markdown
    ]
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

def page_preparation_rendez_vous():
    import streamlit as st
    from interface_assistant import afficher_preparation_rendez_vous

    for fiche in st.session_state["fiches_rdv_test"]:
        afficher_preparation_rendez_vous(fiche)

    st.text("Suite de la page accessible.")


def test_apercus_rendez_vous_independants(monkeypatch):
    import json
    from uuid import uuid4

    import assistant_groq
    from modeles import Appointment

    def appel_interdit(*args, **kwargs):
        pytest.fail("Les aperçus doivent rester locaux.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    premiere = Appointment(
        journey_id=str(uuid4()),
        notes="Notes fictives de la première fiche.",
        questions=("Question de la première fiche ?",),
    )
    seconde = Appointment(
        journey_id=str(uuid4()),
        notes="Notes fictives de la seconde fiche.",
    )

    app = AppTest.from_function(page_preparation_rendez_vous)
    app.session_state["fiches_rdv_test"] = (premiere, seconde)
    app.run()

    assert not app.exception
    assert not app.json

    app.checkbox(
        key=f"preparation_rdv_notes_{premiere.id}"
    ).check().run()
    app.button(
        key=f"preparation_rdv_preparer_{premiere.id}"
    ).click().run()

    assert not app.exception
    assert len(app.json) == 1
    assert not app.checkbox(
        key=f"preparation_rdv_notes_{seconde.id}"
    ).value

    app.checkbox(
        key=f"preparation_rdv_notes_{seconde.id}"
    ).check().run()
    app.button(
        key=f"preparation_rdv_preparer_{seconde.id}"
    ).click().run()

    assert not app.exception
    assert len(app.json) == 2
    apercu_seconde = app.json[1].value

    # Modifier la sélection de la première retire seulement son aperçu.
    app.checkbox(
        key=f"preparation_rdv_questions_{premiere.id}"
    ).check().run()

    assert not app.exception
    assert len(app.json) == 1
    assert app.json[0].value == apercu_seconde

    messages = json.loads(app.json[0].value)
    assert json.loads(messages[1]["content"]) == {
        "contenu_selectionne": {"notes": seconde.notes},
    }
    assert f"preparation_rdv_apercu_{premiere.id}" not in (
        app.session_state
    )
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

@pytest.mark.parametrize(
    "modification",
    [
        {"notes": "Notes fictives modifiées."},
        {"questions": ("Question fictive modifiée ?",)},
    ],
)
def test_modifier_fiche_retire_ancien_apercu(monkeypatch, modification):
    import json
    from dataclasses import replace
    from uuid import uuid4

    import assistant_groq
    from modeles import Appointment

    def appel_interdit(*args, **kwargs):
        pytest.fail("Cette préparation doit rester locale.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    fiche = Appointment(
        journey_id=str(uuid4()),
        notes="Notes fictives initiales.",
        questions=("Question fictive initiale ?",),
    )

    app = AppTest.from_function(page_preparation_rendez_vous)
    app.session_state["fiches_rdv_test"] = (fiche,)
    app.run()

    app.checkbox(
        key=f"preparation_rdv_notes_{fiche.id}"
    ).check().run()
    app.checkbox(
        key=f"preparation_rdv_questions_{fiche.id}"
    ).check().run()
    app.button(
        key=f"preparation_rdv_preparer_{fiche.id}"
    ).click().run()

    assert not app.exception
    assert len(app.json) == 1

    fiche_modifiee = replace(fiche, **modification)
    app.session_state["fiches_rdv_test"] = (fiche_modifiee,)
    app.run()

    assert not app.exception
    assert not app.json
    assert f"preparation_rdv_apercu_{fiche.id}" not in app.session_state

    app.button(
        key=f"preparation_rdv_preparer_{fiche.id}"
    ).click().run()

    assert not app.exception
    messages = json.loads(app.json[0].value)
    assert json.loads(messages[1]["content"]) == {
        "contenu_selectionne": {
            "notes": fiche_modifiee.notes,
            "questions": list(fiche_modifiee.questions),
        },
    }

def page_relecture_rendez_vous():
    import streamlit as st
    from interface_assistant import afficher_relecture_rendez_vous

    nouveau_profil = afficher_relecture_rendez_vous(
        st.session_state["profil_relecture_test"],
        st.session_state["fiche_relecture_test"],
        st.session_state["proposition_relecture_test"],
    )

    if nouveau_profil is not None:
        st.session_state["profil_relecture_test"] = nouveau_profil

    st.text("Suite de la page accessible.")

def test_relecture_exige_confirmation_apres_modification():
    from datetime import date

    from modeles import Appointment, UserProfile

    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 11, 1),
    )
    fiche = Appointment(
        journey_id=profil.active_journey_id,
        notes="Notes originales à conserver.",
        questions=("Question initiale ?",),
    )
    profil = profil.ajouter_rendez_vous(fiche)
    base = f"preparation_rdv_relecture_{fiche.id}"

    app = AppTest.from_function(page_relecture_rendez_vous)
    app.session_state["profil_relecture_test"] = profil
    app.session_state["fiche_relecture_test"] = fiche
    app.session_state["proposition_relecture_test"] = (
        "Question proposée ?",
    )
    app.run()

    assert not app.exception
    assert app.button(key=f"{base}_ajouter").disabled
    assert app.session_state["profil_relecture_test"] == profil

    app.checkbox(key=f"{base}_confirmation").check().run()

    assert not app.exception
    assert not app.button(key=f"{base}_ajouter").disabled
    assert app.session_state["profil_relecture_test"] == profil

    app.text_area(key=f"{base}_texte").set_value(
        "Question modifiée après relecture ?"
    ).run()

    assert not app.exception
    assert not app.checkbox(key=f"{base}_confirmation").value
    assert app.button(key=f"{base}_ajouter").disabled
    assert app.session_state["profil_relecture_test"] == profil

    app.checkbox(key=f"{base}_confirmation").check().run()
    app.button(key=f"{base}_ajouter").click().run()

    assert not app.exception
    nouveau_profil = app.session_state["profil_relecture_test"]
    nouvelle_fiche = nouveau_profil.appointments[0]

    assert nouvelle_fiche.questions == (
        "Question initiale ?",
        "Question modifiée après relecture ?",
    )
    assert nouvelle_fiche.notes == fiche.notes
    assert nouvelle_fiche.id == fiche.id
    assert profil.appointments[0] == fiche
    assert "Suite de la page accessible." in [
        element.value for element in app.text
    ]

def page_proposition_rendez_vous():
    import json
    import streamlit as st
    from interface_assistant import afficher_preparation_rendez_vous

    st.session_state.setdefault("nombre_propositions_test", 0)

    def generer(messages):
        st.session_state["nombre_propositions_test"] += 1
        return json.dumps({
            "questions": ["Question proposée fictive ?"],
        })

    nouveau_profil = afficher_preparation_rendez_vous(
        st.session_state["fiche_proposition_test"],
        profil=st.session_state["profil_proposition_test"],
        generer=generer,
    )

    if nouveau_profil is not None:
        st.session_state["profil_proposition_test"] = nouveau_profil

def test_proposition_puis_ajout_confirme():
    from datetime import date
    from modeles import Appointment, UserProfile

    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 11, 1),
    )
    fiche = Appointment(
        journey_id=profil.active_journey_id,
        notes="Notes originales.",
        questions=("Question initiale ?",),
    )
    profil = profil.ajouter_rendez_vous(fiche)
    base = f"preparation_rdv_relecture_{fiche.id}"

    app = AppTest.from_function(page_proposition_rendez_vous)
    app.session_state["fiche_proposition_test"] = fiche
    app.session_state["profil_proposition_test"] = profil
    app.run()

    app.checkbox(
        key=f"preparation_rdv_notes_{fiche.id}"
    ).check().run()
    app.button(
        key=f"preparation_rdv_preparer_{fiche.id}"
    ).click().run()

    assert not app.exception
    assert app.session_state["nombre_propositions_test"] == 0

    app.button(
        key=f"preparation_rdv_proposer_{fiche.id}"
    ).click().run()

    assert not app.exception
    assert app.session_state["nombre_propositions_test"] == 1
    assert app.session_state["profil_proposition_test"] == profil

    app.run()
    assert app.session_state["nombre_propositions_test"] == 1

    app.checkbox(key=f"{base}_confirmation").check().run()

    # Une nouvelle proposition retire la confirmation précédente.
    app.button(
        key=f"preparation_rdv_proposer_{fiche.id}"
    ).click().run()

    assert not app.exception
    assert app.session_state["nombre_propositions_test"] == 2
    assert not app.checkbox(key=f"{base}_confirmation").value
    assert app.session_state["profil_proposition_test"] == profil

    app.checkbox(key=f"{base}_confirmation").check().run()
    app.button(key=f"{base}_ajouter").click().run()

    assert not app.exception
    nouvelle_fiche = (
        app.session_state["profil_proposition_test"].appointments[0]
    )
    assert nouvelle_fiche.questions == (
        "Question initiale ?",
        "Question proposée fictive ?",
    )
    assert nouvelle_fiche.notes == fiche.notes
    assert app.session_state["nombre_propositions_test"] == 2