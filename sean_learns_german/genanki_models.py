import genanki


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
        {"name": "Conjugation"},
    ],
    templates=[
        {
            "name": "English -> German",
            "qfmt": "{{English}} ({{PartOfSpeech}})",
            "afmt": '{{FrontSide}}<hr id="answer">{{German}}<br /><br />{{Conjugation}}',
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
