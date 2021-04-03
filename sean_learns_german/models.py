import dataclasses
import typing

import genanki
import notion.client
import notion.collection

from sean_learns_german.constants import BankCategory, PartsOfSpeech
from sean_learns_german.genanki_models import GENANKI_NOUN_MODEL, GENANKI_PHRASE_MODEL, GENANKI_VERB_MODEL, GENANKI_VOCABULARY_MODEL
from sean_learns_german.errors import MissingGender, MissingPartOfSpeech


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
