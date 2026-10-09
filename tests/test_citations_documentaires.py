import pytest
import json

from citations_documentaires import (
    extraire_citations,
    trouver_citations_inconnues,
    retrouver_sources_citees,
)


@pytest.mark.parametrize(
    "reponse, attendus",
    [
        (
            "Les rendez-vous figurent ici [calendrier].",
            ("calendrier",),
        ),
        (
            "Le profil [sauvegarde] et les rendez-vous [calendrier]. "
            "Autre mention [sauvegarde].",
            ("sauvegarde", "calendrier"),
        ),
        (
            "Les documents ne permettent pas de répondre.",
            (),
        ),
        (
            "Une référence inconnue [document_invente].",
            ("document_invente",),
        ),
        (
            "Une référence avec espaces [ calendrier ].",
            (" calendrier ",),
        ),
        (
            "Des crochets vides [] ou non fermés [calendrier.",
            (),
        ),
    ],
)
def test_extraire_citations(reponse, attendus):
    assert extraire_citations(reponse) == attendus


@pytest.mark.parametrize("reponse", [None, 42])
def test_extraire_citations_refuse_valeur_non_textuelle(reponse):
    with pytest.raises(ValueError, match="texte"):
        extraire_citations(reponse)


@pytest.mark.parametrize(
    "reponse, contexte, attendus",
    [
        (
            "Les rendez-vous sont affichés [calendrier].",
            '[{"id": "calendrier"}]',
            (),
        ),
        (
            "Le calendrier [calendrier] et le profil [invente].",
            '[{"id": "calendrier"}]',
            ("invente",),
        ),
        (
            "Le profil [invente], puis un autre point [autre]. "
            "Encore le profil [invente].",
            '[{"id": "calendrier"}]',
            ("invente", "autre"),
        ),
        (
            "Les rendez-vous [calendrier].",
            "[]",
            ("calendrier",),
        ),
        (
            "Les documents ne permettent pas de répondre.",
            "[]",
            (),
        ),
        (
            "Les rendez-vous [ calendrier ].",
            '[{"id": "calendrier"}]',
            (" calendrier ",),
        ),
    ],
)
def test_trouver_citations_inconnues(reponse, contexte, attendus):
    assert trouver_citations_inconnues(reponse, contexte) == attendus


def test_sources_conservent_metadonnees_et_ordre_des_citations():
    calendrier = {
        "id": "calendrier",
        "title": "Calendrier fictif",
        "source": "Source fictive A",
        "url": "https://example.org/calendrier",
    }
    sauvegarde = {
        "id": "sauvegarde",
        "title": "Sauvegarde fictive",
        "source": "Source fictive B",
        "url": "https://example.org/sauvegarde",
    }
    contexte = json.dumps(
        [
            {**calendrier, "content": "Les rendez-vous."},
            {**sauvegarde, "content": "Le profil enregistré."},
        ]
    )

    sources = retrouver_sources_citees(
        "Le profil [sauvegarde], les rendez-vous [calendrier], "
        "puis le profil à nouveau [sauvegarde].",
        contexte,
    )

    assert sources == (sauvegarde, calendrier)


def test_sources_refusent_reference_inconnue():
    with pytest.raises(ValueError, match="invente"):
        retrouver_sources_citees(
            "Une information [invente].",
            "[]",
        )


def test_sources_vides_sans_citation():
    assert retrouver_sources_citees(
        "Les documents sont insuffisants.",
        "[]",
    ) == ()

def test_sources_refusent_melange_valide_et_inconnu():
    contexte = json.dumps(
        [
            {
                "id": "calendrier",
                "title": "Calendrier fictif",
                "content": "Le calendrier présente les rendez-vous.",
                "source": "Source fictive",
                "url": "https://example.org/calendrier",
            },
        ]
    )
    reponse = (
        "Les rendez-vous sont affichés [calendrier]. "
        "Une autre information est disponible [invente]."
    )

    with pytest.raises(ValueError, match="invente"):
        retrouver_sources_citees(reponse, contexte)

