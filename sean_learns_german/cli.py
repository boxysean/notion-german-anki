import dataclasses
import enum
import logging
import typing

import click
import genanki
import notion.client
import notion.collection


from sean_learns_german.models import GermanBankItem, GermanBankVocabulary, GermanBankNoun, GermanBankVerb, GermanBankPhrase, GermanNote
from sean_learns_german.constants import BankCategory, PartsOfSpeech
from sean_learns_german.errors import MissingGender, MissingPartOfSpeech


logging.basicConfig(
    level=logging.INFO,
)


NOTION_GERMAN_BANK_VIEW_URL = "https://www.notion.so/0bf4b6fd23af40dba8d4c23206b2f1e3?v=e2f51d7caf4a43c7a791304984f019bb"


@click.group()
def cli():
    pass


@cli.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
@click.option("--output-filename", type=str, default="output.apkg")
def generate_decks(token: str, output_filename: str) -> None:
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



if __name__ == "__main__":
    cli()
