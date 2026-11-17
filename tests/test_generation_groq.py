import pytest
import httpx
from types import SimpleNamespace

import generation_groq
from assistant_documentaire import GenerationIndisponible


def test_generation_groq_transmet_parametres_et_ferme_client(monkeypatch):
    configuration = {}
    appels = []
    fermetures = []

    messages = (
        {"role": "system", "content": "Utilise les documents fournis."},
        {"role": "user", "content": "Question et documents fictifs."},
    )

    class FauxClient:
        def __init__(self, **options):
            configuration.update(options)
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.creer)
            )

        def __enter__(self):
            return self

        def __exit__(self, type_erreur, erreur, trace):
            fermetures.append(True)

        def creer(self, **parametres):
            appels.append(parametres)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        finish_reason="stop",
                        message=SimpleNamespace(
                            content="Réponse fictive [calendrier]."
                        ),
                    )
                ]
            )

    monkeypatch.setattr(generation_groq, "Groq", FauxClient)

    reponse = generation_groq.generer_reponse_groq(
        messages,
        cle_api="cle-fictive",
        modele="modele-fictif",
    )

    assert reponse == "Réponse fictive [calendrier]."
    assert configuration == {
        "api_key": "cle-fictive",
        "timeout": 20.0,
        "max_retries": 0,
    }
    assert appels == [
        {
            "model": "modele-fictif",
            "messages": list(messages),
            "max_completion_tokens": 1024,
            "stream": False,
        }
    ]
    assert fermetures == [True]

@pytest.mark.parametrize(
    "raison, texte, exception_attendue, erreur_attendue",
    [
        (
            None,
            None,
            generation_groq.ReponseGroqVide,
            "aucune réponse",
        ),
        (
            "length",
            "Texte interrompu [calendrier]",
            generation_groq.GenerationGroqInterrompue,
            "normalement",
        ),
        (
            "tool_calls",
            None,
            generation_groq.GenerationGroqInterrompue,
            "normalement",
        ),
        (
            "stop",
            None,
            generation_groq.ReponseGroqVide,
            "texte exploitable",
        ),
        (
            "stop",
            "",
            generation_groq.ReponseGroqVide,
            "texte exploitable",
        ),
        (
            "stop",
            "   ",
            generation_groq.ReponseGroqVide,
            "texte exploitable",
        ),
    ],
)
def test_generation_groq_refuse_reponse_inexploitable(
    monkeypatch,
    raison,
    texte,
    exception_attendue,
    erreur_attendue,
):
    choix = []

    if raison is not None:
        choix.append(
            SimpleNamespace(
                finish_reason=raison,
                message=SimpleNamespace(content=texte),
            )
        )

    class FauxClient:
        def __init__(self, **options):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **parametres: SimpleNamespace(
                        choices=choix
                    )
                )
            )

        def __enter__(self):
            return self

        def __exit__(self, type_erreur, erreur, trace):
            return False

    monkeypatch.setattr(generation_groq, "Groq", FauxClient)

    with pytest.raises(exception_attendue, match=erreur_attendue):
        generation_groq.generer_reponse_groq(
            (
                {"role": "user", "content": "Question fictive"},
            ),
            cle_api="cle-fictive",
            modele="modele-fictif",
        )

@pytest.mark.parametrize(
    "statut, exception_attendue, message_attendu",
    [
        (
            None,
            GenerationIndisponible,
            "Connexion à Groq indisponible.",
        ),
        (
            408,
            GenerationIndisponible,
            "Service Groq temporairement indisponible.",
        ),
        (
            429,
            GenerationIndisponible,
            "Service Groq temporairement indisponible.",
        ),
        (
            503,
            GenerationIndisponible,
            "Service Groq temporairement indisponible.",
        ),
        (
            401,
            generation_groq.RequeteGroqRefusee,
            "La requête Groq a été refusée. Vérifier la configuration de la clé et du modèle.",
        ),
        (
            400,
            generation_groq.RequeteGroqRefusee,
            "La requête Groq a été refusée. Vérifier la configuration de la clé et du modèle.",
        ),
    ],
)
def test_generation_groq_traduit_erreurs(
    monkeypatch,
    statut,
    exception_attendue,
    message_attendu,
):
    requete = httpx.Request("POST", "https://example.org/generation")
    fermetures = []

    if statut is None:
        erreur_fournisseur = generation_groq.APIConnectionError(
            request=requete,
        )
    else:
        erreur_fournisseur = generation_groq.APIStatusError(
            "Détail technique fictif",
            response=httpx.Response(statut, request=requete),
            body={"detail": "Détail technique fictif"},
        )

    class FauxClient:
        def __init__(self, **options):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.creer)
            )

        def __enter__(self):
            return self

        def __exit__(self, type_erreur, erreur, trace):
            fermetures.append(True)
            return False

        def creer(self, **parametres):
            raise erreur_fournisseur

    monkeypatch.setattr(generation_groq, "Groq", FauxClient)

    with pytest.raises(exception_attendue) as erreur_capturee:
        generation_groq.generer_reponse_groq(
            ({"role": "user", "content": "Question fictive"},),
            cle_api="cle-fictive",
            modele="modele-fictif",
        )

    assert str(erreur_capturee.value) == message_attendu
    assert fermetures == [True]

@pytest.mark.parametrize(
    "messages, cle_api, modele, erreur_attendue",
    [
        ((), "cle-fictive", "modele-fictif", "messages"),
        (
            ({"role": "user", "content": "Question fictive"},),
            "",
            "modele-fictif",
            "clé API",
        ),
        (
            ({"role": "user", "content": "Question fictive"},),
            "   ",
            "modele-fictif",
            "clé API",
        ),
        (
            ({"role": "user", "content": "Question fictive"},),
            None,
            "modele-fictif",
            "clé API",
        ),
        (
            ({"role": "user", "content": "Question fictive"},),
            "cle-fictive",
            "",
            "modèle",
        ),
        (
            ({"role": "user", "content": "Question fictive"},),
            "cle-fictive",
            "   ",
            "modèle",
        ),
        (
            ({"role": "user", "content": "Question fictive"},),
            "cle-fictive",
            None,
            "modèle",
        ),
    ],
)
def test_generation_groq_refuse_configuration_avant_client(
    monkeypatch,
    messages,
    cle_api,
    modele,
    erreur_attendue,
):
    def creation_interdite(**options):
        pytest.fail("Le client Groq ne devait pas être créé.")

    monkeypatch.setattr(generation_groq, "Groq", creation_interdite)

    with pytest.raises(ValueError, match=erreur_attendue):
        generation_groq.generer_reponse_groq(
            messages,
            cle_api=cle_api,
            modele=modele,
        )

def test_appel_rendez_vous_differe_et_transmet_messages(monkeypatch):
    appels = []
    messages = ({"role": "user", "content": "Notes fictives."},)

    def faux_appel(messages, *, cle_api, modele):
        appels.append((messages, cle_api, modele))
        return "PREPARATION_AUTORISEE"

    monkeypatch.setattr(generation_groq, "generer_reponse_groq", faux_appel)

    appeler = generation_groq.creer_appel_groq_rendez_vous(
        cle_api="cle-fictive",
        modele="modele-fictif",
    )

    assert appels == []
    assert appeler(messages) == "PREPARATION_AUTORISEE"
    assert appels == [(messages, "cle-fictive", "modele-fictif")]


@pytest.mark.parametrize(
    "type_erreur",
    [
        generation_groq.RequeteGroqRefusee,
        generation_groq.GenerationGroqInterrompue,
        generation_groq.ReponseGroqVide,
    ],
)
def test_appel_rendez_vous_masque_erreur_fournisseur(monkeypatch, type_erreur):
    def faux_appel(*args, **kwargs):
        raise type_erreur("DETAIL_TECHNIQUE_NON_PUBLIC")

    monkeypatch.setattr(generation_groq, "generer_reponse_groq", faux_appel)

    appeler = generation_groq.creer_appel_groq_rendez_vous(
        cle_api="cle-fictive",
        modele="modele-fictif",
    )

    with pytest.raises(GenerationIndisponible) as erreur:
        appeler(({"role": "user", "content": "Notes fictives."},))

    assert "DETAIL_TECHNIQUE_NON_PUBLIC" not in str(erreur.value)