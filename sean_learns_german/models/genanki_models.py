import genanki


class GermanNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


GENANKI_CSS = """.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}"""

GENANKI_VOCABULARY_MODEL = genanki.Model(
    model_id=1557451532,  # hard coded
    name="German Vocabulary Model",
    fields=[
        {"name": "German"},
        {"name": "English"},
        {"name": "PartOfSpeech"},
    ],
    templates=[
        {
            "name": "English -> German",
            "qfmt": "{{English}} ({{PartOfSpeech}})",
            "afmt": '{{FrontSide}}<hr id="answer">{{German}}',
        },
        {
            "name": "German -> English",
            "qfmt": "{{German}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}} ({{PartOfSpeech}})',
        },
    ],
    css=GENANKI_CSS,
)

GENANKI_NOUN_MODEL = genanki.Model(
    model_id=1244371399,  # hard coded
    name="German Noun Model",
    fields=[
        {"name": "German"},
        {"name": "English"},
        {"name": "PartOfSpeech"},
        {"name": "Gender"},
    ],
    templates=[
        {
            "name": "English -> German",
            "qfmt": "{{English}} ({{PartOfSpeech}})",
            "afmt": '{{FrontSide}}<hr id="answer">{{Gender}} {{German}}',
        },
        {
            "name": "German -> English",
            "qfmt": "{{Gender}} {{German}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}} ({{PartOfSpeech}})',
        },
    ],
    css=GENANKI_CSS,
)


GENANKI_VERB_MODEL = genanki.Model(
    model_id=2064417967,  # hard coded
    name="German Verb Model",
    fields=[
        {"name": "German"},
        {"name": "English"},
        {"name": "PartOfSpeech"},
        {"name": "Conjugation (ich)"},
        {"name": "Conjugation (du)"},
        {"name": "Conjugation (er/sie/es)"},
        {"name": "Conjugation (wir)"},
        {"name": "Conjugation (ihr)"},
        {"name": "Conjugation (Sie)"},
    ],
    templates=[
        {
            "name": "English -> German",
            "qfmt": "{{English}} ({{PartOfSpeech}})",
            "afmt": '{{FrontSide}}<hr id="answer">{{German}}<br /><br />ich {{Conjugation (ich)}}, du {{Conjugation (du)}}, er/sie/es {{Conjugation (er/sie/es)}}, wir {{Conjugation (wir)}}, ihr {{Conjugation (ihr)}}, Sie {{Conjugation (Sie)}}',
        },
        {
            "name": "German -> English",
            "qfmt": "{{German}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}} ({{PartOfSpeech}})',
        },
    ],
    css=GENANKI_CSS,
)


GENANKI_PHRASE_MODEL = genanki.Model(
    model_id=1618410619,  # hard coded
    name="German Phrase Model",
    fields=[
        {"name": "German"},
        {"name": "English"},
    ],
    templates=[
        {
            "name": "English -> German",
            "qfmt": "{{English}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{German}}',
        },
        {
            "name": "German -> English",
            "qfmt": "{{German}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}}',
        },
    ],
    css=GENANKI_CSS,
)
