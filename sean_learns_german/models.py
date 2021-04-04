import dataclasses
import typing

import genanki
import notion.client
import notion.collection

from sean_learns_german.constants import BankCategory, PartsOfSpeech, NounGender, SpeechPerspective
from sean_learns_german.genanki_models import GermanNote, GENANKI_NOUN_MODEL, GENANKI_PHRASE_MODEL, GENANKI_VERB_MODEL, GENANKI_VOCABULARY_MODEL
from sean_learns_german.errors import MissingGender, MissingPartOfSpeech


@dataclasses.dataclass
class GermanBankItem:
    category: str
    anki_ignore: bool
    german: str
    english: str
    tags: typing.List[str]

    @classmethod
    def make(cls, **kwargs):
        return cls(
            anki_ignore=False,
            tags=[],
            **kwargs
        )

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
                conj_ich_1ps=row.conj_ich_1ps,
                conj_du_2ps=row.conj_du_2ps,
                conj_er_3ps=row.conj_er_3ps,
                conj_wir_1pp=row.conj_wir_1pp,
                conj_ihr_2pp=row.conj_ihr_2pp,
                conj_sie_3pp=row.conj_sie_3pp,
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
    gender: NounGender
    plural: str

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
    requires_accusative: bool
    conj_ich_1ps: str
    conj_du_2ps: str
    conj_er_3ps: str
    conj_wir_1pp: str
    conj_ihr_2pp: str
    conj_sie_3pp: str

    def to_german_note(self) -> GermanNote:
        return GermanNote(
            model=GENANKI_VERB_MODEL,
            fields=[
                self.german,
                self.english,
                self.part_of_speech,
                self.conj_ich_1ps,
                self.conj_du_2ps,
                self.conj_er_3ps,
                self.conj_wir_1pp,
                self.conj_ihr_2pp,
                self.conj_sie_3pp,
            ],
            tags=[self.part_of_speech] + self.tags,
        )

    def conjugate(self, perspective: SpeechPerspective):
        if perspective == SpeechPerspective.FIRST_PERSON_SINGULAR:
            return self.conj_ich_1ps
        elif perspective == SpeechPerspective.SECOND_PERSON_SINGULAR:
            return self.conj_du_2ps
        elif perspective == SpeechPerspective.THIRD_PERSON_SINGULAR:
            return self.conj_er_3ps
        elif perspective == SpeechPerspective.FIRST_PERSON_PLURAL:
            return self.conj_wir_1pp
        elif perspective == SpeechPerspective.SECOND_PERSON_PLURAL:
            return self.conj_ihr_2pp
        elif perspective == SpeechPerspective.THIRD_PERSON_PLURAL:
            return self.conj_sie_3pp
        else:
            raise ValueError(perspective)


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
