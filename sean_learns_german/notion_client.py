import logging
import typing

import notion.client

from sean_learns_german.constants import BankCategory, PartsOfSpeech
from sean_learns_german.errors import MissingCategory, MissingGender, MissingPartOfSpeech
from sean_learns_german.models.german_models import BankWord, BankNoun, BankVocabulary, Phrase, Verb


NOTION_GERMAN_BANK_VIEW_URL = "https://www.notion.so/0bf4b6fd23af40dba8d4c23206b2f1e3?v=e2f51d7caf4a43c7a791304984f019bb"


class GermanBankNotionClient(notion.client.NotionClient):
    def _parse_row(self, row: notion.collection.CollectionRowBlock) -> typing.Union[BankWord, Phrase]:
        if row.category is None:
            raise MissingCategory()

        if row.category == BankCategory.PHRASE:
            return Phrase(
                german=row.german,
                english=row.english,
                tags=row.tags,
            )
        elif row.part_of_speech == PartsOfSpeech.NOUN:
            return BankNoun(
                german_word_singular=row.german,
                german_word_plural=row.german_plural,
                english_word=row.english,
                gender=row.gender,
                tags=row.tags,
            )
        elif row.part_of_speech == PartsOfSpeech.VERB:
            return Verb(
                german_word=row.german,
                english_word=row.english,
                conj_ich_1ps=row.conj_ich_1ps,
                conj_du_2ps=row.conj_du_2ps,
                conj_er_3ps=row.conj_er_3ps,
                conj_wir_1pp=row.conj_wir_1pp,
                conj_ihr_2pp=row.conj_ihr_2pp,
                conj_sie_3pp=row.conj_sie_3pp,
                requires_case=row.requires_case,
                tags=row.tags,
            )
        else:
            return BankVocabulary(
                german=row.german,
                english=row.english,
                part_of_speech=row.part_of_speech,
                tags=row.tags,
            )

    def load_bank_items(self) -> typing.Generator[typing.Union[BankWord, Phrase], None, None]:
        view = self.get_collection_view(NOTION_GERMAN_BANK_VIEW_URL)

        for row in view.collection.get_rows():
            try:
                german_bank_item = self._parse_row(row)
            except MissingPartOfSpeech:
                logging.warning("%s is missing part of speech, skipping...", row.german)
                continue
            except MissingGender:
                logging.warning("%s is missing gender, skipping...", row.german)
                continue
            except MissingCategory:
                logging.warning("%s is missing category, skipping...", row.german)
                continue

            if 'anki ignore' in german_bank_item.tags:
                continue

            yield german_bank_item

    def get_bank_verbs(self) -> typing.List[Verb]:
        return [
            german_bank_item
            for german_bank_item in self.load_bank_items()
            if isinstance(german_bank_item, Verb)
        ]

    def get_bank_nouns(self) -> typing.List[BankNoun]:
        return [
            german_bank_item
            for german_bank_item in self.load_bank_items()
            if isinstance(german_bank_item, BankNoun)
        ]
