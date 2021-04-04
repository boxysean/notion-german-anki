import dataclasses
import enum
import logging
import random
import typing

import click
import genanki
import notion.client
import notion.collection


from sean_learns_german.constants import BankCategory, PartsOfSpeech, GermanCase, SpeechPerspective, ArticleType, NounGender, PronounType, Cardinality
from sean_learns_german.errors import MissingGender, MissingPartOfSpeech
from sean_learns_german.models.notion_models import GermanBankItem, GermanBankVocabulary, GermanBankNoun, GermanBankVerb, GermanBankPhrase, BANK_NOUNS, BANK_VERBS
from sean_learns_german.models.genanki_models import GermanNote
from sean_learns_german.models.german_models import ArticledNoun, Pronoun, Verb


logging.basicConfig(
    level=logging.INFO,
)


NOTION_GERMAN_BANK_VIEW_URL = "https://www.notion.so/0bf4b6fd23af40dba8d4c23206b2f1e3?v=e2f51d7caf4a43c7a791304984f019bb"


@click.group()
def cli_group():
    pass


@cli_group.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
@click.option("--output-filename", type=str, default="output.apkg")
def generate_decks(token: str, output_filename: str) -> None:
    """
    Scrapes the Notion table bank, and converts them into Anki decks ready for importing.
    """

    client = notion.client.NotionClient(token_v2=token)
    view = client.get_collection_view(NOTION_GERMAN_BANK_VIEW_URL)

    decks = {
        BankCategory.VOCABULARY: genanki.Deck(
            deck_id=1854703173,  # Hard-coded value selected by me
            name="German::Vocabulary",
        ),
        BankCategory.PHRASE: genanki.Deck(
            deck_id=1568577201,  # Hard-coded value selected by me
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

    genanki.Package(decks.values()).write_to_file(output_filename)
    click.echo(f"Complete! Now import {output_filename} to Anki, fix any changes, and sync Anki to AnkiCloud.")


@cli_group.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
@click.option("--output-filename", type=str, default="sentences_output.apkg")
def generate_sentences(token: str, output_filename: str):
    """
    Generates sentences
    """

    # client = notion.client.NotionClient(token_v2=token)
    # view = client.get_collection_view(NOTION_GERMAN_BANK_VIEW_URL)
    # rows = view.collection.get_rows()

    # nouns = []
    # verbs = []

    # for row in view.collection.get_rows():
    #     try:
    #         german_bank_item = GermanBankItem.from_notion_row(row)
    #     except MissingPartOfSpeech:
    #         logging.warning("%s is missing part of speech, skipping...", row.german)
    #         continue
    #     except MissingGender:
    #         logging.warning("%s is missing gender, skipping...", row.german)
    #         continue

    #     if german_bank_item.anki_ignore:
    #         continue

    #     if not isinstance(german_bank_item, GermanBankVocabulary):
    #         # Get rid of phrases
    #         continue

    #     if german_bank_item.part_of_speech == 'noun':
    #         nouns.append(german_bank_item)
    #     elif german_bank_item.part_of_speech == 'verb' and german_bank_item.conj_ich_1ps and german_bank_item.conj_du_2ps and german_bank_item.conj_er_3ps and german_bank_item.conj_wir_1pp and german_bank_item.conj_ihr_2pp and german_bank_item.conj_sie_3pp:
    #         if german_bank_item.german in ['sein', 'mögen', 'haben', 'sehen', 'suchen', 'finden', 'essen']:
    #             verbs.append(german_bank_item)

    # print(f"{len(nouns)} nouns and {len(verbs)} verbs")

    def generate_sentence(nouns: typing.List[GermanBankNoun], verbs: typing.List[GermanBankVerb]) -> str:
        # https://iwillteachyoualanguage.com/learn/german/german-tips/german-cases-explained
        subject_is_pronoun = random.choice([False, True])

        if subject_is_pronoun:
            subject = Pronoun.random()
        else:
            subject = ArticledNoun.random(nouns=nouns)

        random_verb = Verb.random(verbs=verbs)
        object_ = ArticledNoun.random(nouns=nouns)

        answer_sentence = (
            f"{subject.make_str(case=GermanCase.NOMINATIVE)} "
            f"{random_verb.conjugate(subject.perspective, subject.cardinality)} "
            f"{object_.make_str(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)}"
        )

        blank_it = random.choice(['subject', 'verb', 'object'])

        if blank_it == 'subject':
            question_sentence = (
                "____ "
                f"{random_verb.conjugate(subject.perspective, subject.cardinality)} "
                f"{object_.make_str(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)} "
                f"{subject.blank_it(case=GermanCase.NOMINATIVE)}"
            )
        elif blank_it == 'verb':
            question_sentence = (
                f"{subject.make_str(case=GermanCase.NOMINATIVE)} "
                "____ "
                f"{object_.make_str(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)} "
                f"({random_verb.german_word})"
            )
        elif blank_it == 'object':
            question_sentence = (
                f"{subject.make_str(case=GermanCase.NOMINATIVE)} "
                f"{random_verb.conjugate(subject.perspective, subject.cardinality)} "
                f"____ "
                f"{object_.blank_it(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)}"
            )

        # return question_sentence
        print(question_sentence[0].upper() + question_sentence[1:])
        print(answer_sentence[0].upper() + answer_sentence[1:])
        print()

    # TODO: sometimes add an adjective?
    # TODO: make questions?
    for i in range(25):
        generate_sentence(BANK_NOUNS, BANK_VERBS)


if __name__ == "__main__":
    cli_group()
