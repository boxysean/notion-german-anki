import logging
import requests
import typing

from sean_learns_german.constants import BankCategory, GermanCase, NounGender, PartsOfSpeech
from sean_learns_german.errors import MissingCategory, MissingGender, MissingGerman, MissingPartOfSpeech
from sean_learns_german.models.german_models import BankWord, BankNoun, BankVocabulary, Phrase, Verb


NOTION_GERMAN_BANK_DATABASE_ID = "0bf4b6fd23af40dba8d4c23206b2f1e3"


class GermanBankNotionClient:
    def __init__(self, token: str):
        self._token = token

    def _parse_property(self, property_dict: dict) -> typing.Optional[str]:
        if property_dict['type'] == 'title':
            try:
                return self._parse_property(property_dict['title'][0])
            except IndexError:
                raise MissingGerman()
        elif property_dict['type'] == 'rich_text':
            if property_dict['rich_text']:
                return self._parse_property(property_dict['rich_text'][0])
            else:
                return None
        elif property_dict['type'] == 'text':
            return property_dict['plain_text']
        elif property_dict['type'] == 'select':
            if property_dict['select']:
                return property_dict['select']['name']
            else:
                return None
        else:
            raise Exception(f"Unknown property type '{property_dict['type']}'")

    def _parse_result(self, result: dict) -> typing.Union[BankWord, Phrase]:
        if result['properties']['Category'] is None:
            raise MissingCategory()

        category = self._parse_property(result['properties']['Category'])
        part_of_speech = self._parse_property(result['properties']['Part of speech'])

        if category == BankCategory.PHRASE:
            return Phrase(
                german=self._parse_property(result['properties']['German']),
                english=self._parse_property(result['properties']['English']),
                # tags=row.tags,
                tags=[],
            )
        elif part_of_speech == PartsOfSpeech.NOUN:
            return BankNoun(
                german_word_singular=self._parse_property(result['properties']['German']),
                german_word_plural=self._parse_property(result['properties']['German plural']),
                english_word=self._parse_property(result['properties']['English']),
                gender=NounGender.from_string(self._parse_property(result['properties']['Gender'])),
                # tags=row.tags,
                tags=[],
            )
        elif part_of_speech == PartsOfSpeech.VERB:
            return Verb(
                german_word=self._parse_property(result['properties']['German']),
                english_word=self._parse_property(result['properties']['English']),
                conj_ich_1ps=self._parse_property(result['properties']['Conj (ich/1PS)']),
                conj_du_2ps=self._parse_property(result['properties']['Conj (du/2PS)']),
                conj_er_3ps=self._parse_property(result['properties']['Conj (er/3PS)']),
                conj_wir_1pp=self._parse_property(result['properties']['Conj (wir/1PP)']),
                conj_ihr_2pp=self._parse_property(result['properties']['Conj (ihr/2PP)']),
                conj_sie_3pp=self._parse_property(result['properties']['Conj (Sie/3PP)']),
                requires_case=GermanCase.from_string(self._parse_property(result['properties']['Requires case'])),
                # tags=row.tags,
                tags=[],
            )
        else:
            return BankVocabulary(
                german=self._parse_property(result['properties']['German']),
                english=self._parse_property(result['properties']['English']),
                part_of_speech=self._parse_property(result['properties']['Part of speech']),
                # tags=row.tags,
                tags=[],
            )

    def load_bank_items(self) -> typing.Generator[typing.Union[BankWord, Phrase], None, None]:
        start_cursor: typing.Optional[str] = None
        has_more = True

        while has_more:
            send_json = {'page_size': 100}
            if start_cursor:
                send_json['start_cursor'] = start_cursor

            response = requests.post(
                url=f"https://api.notion.com/v1/databases/{NOTION_GERMAN_BANK_DATABASE_ID}/query",
                headers={
                    'Authorization': f"Bearer {self._token}",
                    'Notion-Version': '2021-08-16',
                    'Content-Type': 'application/json',
                },
                json=send_json,
            )

            response.raise_for_status()
            data = response.json()

            for result in data['results']:
                try:
                    german_bank_item = self._parse_result(result)
                except TypeError as e:
                    # import pdb; pdb.set_trace()
                    logging.warning("Skipping %s: %s", self._parse_property(result['properties']['German']), str(e))
                    continue
                except MissingGerman:
                    logging.warning("%s is missing german, skipping...", result['properties']['German'])
                    continue
                except MissingPartOfSpeech:
                    logging.warning("%s is missing part of speech, skipping...", result['properties']['German'])
                    continue
                except MissingGender:
                    logging.warning("%s is missing gender, skipping...", result['properties']['German'])
                    continue
                except MissingCategory:
                    logging.warning("%s is missing category, skipping...", result['properties']['German'])
                    continue

                if 'anki ignore' in german_bank_item.tags:
                    continue

                yield german_bank_item

                has_more = data['has_more']
                # has_more = False
                start_cursor = data['next_cursor']

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
