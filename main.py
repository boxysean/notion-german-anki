import dataclasses
import enum
import logging
import typing

import click
import genanki
import notion.client
import notion.collection


logging.basicConfig(
    level=logging.INFO,
)


class BankCategory(str, enum.Enum):
    VOCABULARY = "Vocabulary"
    PHRASE = "Phrase"


class PartsOfSpeech(str, enum.Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    CONJUNCTION = "conjunction"
    NUMBER = "number"


class MissingPartOfSpeech(ValueError):
    pass


class MissingGender(ValueError):
    pass


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


class GermanNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


@dataclasses.dataclass
class GermanBankItem:
    category: str
    anki_ignore: bool
    german: str
    english: str
    tags: typing.List[str]

    @classmethod
    def from_notion_row(cls, row: notion.collection.CollectionRowBlock) -> "GermanBankItem":
        if row.category == BankCategory.PHRASE:
            return GermanBankPhrase(
                category=row.category,
                anki_ignore=row.anki_ignore,
                german=row.german,
                english=row.english,
                tags=row.tags,
            )
        elif row.part_of_speech == PartsOfSpeech.NOUN:
            return GermanBankNoun(
                category=row.category,
                anki_ignore=row.anki_ignore,
                german=row.german,
                english=row.english,
                part_of_speech=row.part_of_speech,
                gender=row.gender,
                tags=row.tags,
            )
        elif row.part_of_speech == PartsOfSpeech.VERB:
            return GermanBankVerb(
                category=row.category,
                anki_ignore=row.anki_ignore,
                german=row.german,
                english=row.english,
                part_of_speech=row.part_of_speech,
                conjugation=row.conjugation,
                tags=row.tags,
            )
        else:
            return GermanBankVocabulary(
                category=row.category,
                anki_ignore=row.anki_ignore,
                german=row.german,
                english=row.english,
                part_of_speech=row.part_of_speech,
                tags=row.tags,
            )

    def to_german_note(self) -> GermanNote:
        return GermanNote(
            model=GENANKI_VOCABULARY_MODEL,
            fields=[
                self.german,
                self.english,
                self.part_of_speech,
            ],
            tags=[self.part_of_speech] + self.tags,
        )


@dataclasses.dataclass
class GermanBankVocabulary(GermanBankItem):
    part_of_speech: PartsOfSpeech

    def __post_init__(self):
        if not self.part_of_speech:
            raise MissingPartOfSpeech()

    def to_german_note(self) -> GermanNote:
        return GermanNote(
            model=GENANKI_VOCABULARY_MODEL,
            fields=[
                self.german,
                self.english,
                self.part_of_speech,
            ],
            tags=[self.part_of_speech] + self.tags,
        )


@dataclasses.dataclass
class GermanBankNoun(GermanBankVocabulary):
    part_of_speech: PartsOfSpeech
    gender: str

    def __post_init__(self):
        super().__post_init__()
        if not self.gender:
            raise MissingGender()

    def to_german_note(self) -> GermanNote:
        return GermanNote(
            model=GENANKI_NOUN_MODEL,
            fields=[
                self.german,
                self.english,
                self.part_of_speech,
                self.gender,
            ],
            tags=[self.part_of_speech] + self.tags,
        )


@dataclasses.dataclass
class GermanBankVerb(GermanBankVocabulary):
    part_of_speech: PartsOfSpeech
    conjugation: str

    def to_german_note(self) -> GermanNote:
        return GermanNote(
            model=GENANKI_VERB_MODEL,
            fields=[
                self.german,
                self.english,
                self.part_of_speech,
                self.conjugation,
            ],
            tags=[self.part_of_speech] + self.tags,
        )


@dataclasses.dataclass
class GermanBankPhrase(GermanBankItem):
    def to_german_note(self) -> GermanNote:
        return GermanNote(
            model=GENANKI_PHRASE_MODEL,
            fields=[
                self.german,
                self.english,
            ],
            tags=self.tags,
        )


@click.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
def main(token: str) -> None:
    client = notion.client.NotionClient(token_v2=token)
    view = client.get_collection_view("https://www.notion.so/0bf4b6fd23af40dba8d4c23206b2f1e3?v=e2f51d7caf4a43c7a791304984f019bb")

    decks = {
        BankCategory.VOCABULARY: genanki.Deck(
            deck_id=1854703173,
            name="German::Vocabulary",
        ),
        BankCategory.PHRASE: genanki.Deck(
            deck_id=1568577201,
            name="German::Phrases",
        ),
    }

    for row in view.collection.get_rows():
        try:
            german_bank_item = GermanBankItem.from_notion_row(row)
        except MissingPartOfSpeech:
            logging.warning("%s is missing part of speech, skipping...", row.german)
            continue
        except MissingGender:
            logging.warning("%s is missing gender, skipping...", row.german)
            continue

        german_note = german_bank_item.to_german_note()

        if german_bank_item.anki_ignore:
            continue

        if not german_bank_item.category:
            logging.warning("%s is missing category, skipping", german_bank_item.german)
        else:
            decks[german_bank_item.category].add_note(german_note)

    genanki.Package(decks.values()).write_to_file('output.apkg')


if __name__ == "__main__":
    main()
