import typing

import genanki

from sean_learns_german.models.german_models import BankWord, Phrase


class GermanNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])

    @classmethod
    def from_german_model(cls, german_model: typing.Union[BankWord, Phrase]) -> 'GermanNote':
        if isinstance(german_model, BankVerb):
            return cls(
                model=GENANKI_VERB_MODEL,
                fields=[
                    german_model.german,
                    german_model.english,
                    german_model.part_of_speech,
                    german_model.conj_ich_1ps,
                    german_model.conj_du_2ps,
                    german_model.conj_er_3ps,
                    german_model.conj_wir_1pp,
                    german_model.conj_ihr_2pp,
                    german_model.conj_sie_3pp,
                ],
                tags=[german_model.part_of_speech] + german_model.tags,
            )
        elif isinstance(german_model, BankNoun):
            return GermanNote(
                model=GENANKI_NOUN_MODEL,
                fields=[
                    german_model.german,
                    german_model.english,
                    german_model.part_of_speech,
                    german_model.gender,
                ],
                tags=[german_model.part_of_speech] + german_model.tags,
            )
        elif isinstance(german_model, BankVocabulary):
            return GermanNote(
                model=GENANKI_VOCABULARY_MODEL,
                fields=[
                    self.german,
                    self.english,
                    self.part_of_speech,
                ],
                tags=[self.part_of_speech] + self.tags,
            )
        elif isinstance(german_model, Phrase):
            return GermanNote(
                model=GENANKI_PHRASE_MODEL,
                fields=[
                    self.german,
                    self.english,
                ],
                tags=self.tags,
            )
        else:
            raise ValueError(f"Unexpected model of type {german_model.__class__.__name__}")


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


GENANKI_GRAMMAR_MODEL = genanki.Model(
    model_id=1572189083,  # hard coded
    name="German Grammar Model",
    fields=[
        {"name": "Complete sentence"},
        {"name": "Incomplete sentence"},
        {"name": "English sentence"},
        {"name": "Hint"},
        {"name": "Format"},
    ],
    templates=[
        {
            "name": "Complete the sentence",
            "qfmt": "{{Incomplete sentence}}{{#Hint}} ({{Hint}}){{/Hint}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Complete sentence}}',
        },
    ],
    css=GENANKI_CSS,
)
