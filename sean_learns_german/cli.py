import logging

import click
import genanki

from sean_learns_german.constants import BankCategory
from sean_learns_german.errors import MissingGermanPluralWord
from sean_learns_german.models.genanki_models import GermanNote
from sean_learns_german.models.german_models import BankWord, Phrase
from sean_learns_german.models.basic_sentence import BasicSentence
from sean_learns_german.notion_client import GermanBankNotionClient
from sean_learns_german.play import play
from sean_learns_german.words import BANK_NOUNS, BANK_VERBS


logging.basicConfig(
    level=logging.INFO,
)


@click.group()
def cli_group():
    pass


@cli_group.command()
@click.option(
    "--token",
    type=str,
    help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so",
    required=True,
    envvar="NOTION_API_TOKEN",
)
@click.option(
    "--output-filename",
    type=str,
    default="output.apkg",
)
def generate_decks(token: str, output_filename: str) -> None:
    """
    Scrapes the Notion table bank, and converts them into Anki decks ready for importing.
    """
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

    for german_bank_item in GermanBankNotionClient(token).load_bank_items():
        if isinstance(german_bank_item, BankWord):
            deck = decks[BankCategory.VOCABULARY]
        elif isinstance(german_bank_item, Phrase):
            deck = decks[BankCategory.PHRASE]
        else:
            raise ValueError(f"Unexpected bank item {german_bank_item}")

        german_note = GermanNote.from_german_model(german_bank_item)
        deck.add_note(german_note)

    genanki.Package(decks.values()).write_to_file(output_filename)
    click.echo(f"Complete! Now import {output_filename} to Anki, fix any changes, and sync Anki to AnkiCloud.")


@cli_group.command()
@click.option(
    "--token",
    type=str,
    help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so",
)
@click.option("--online/--offline", default=True, help="")
@click.option("--output-filename", type=str, default="grammar_output.apkg")
def generate_sentences(token: str, output_filename: str, online: bool):
    """
    Generates sentences
    """
    notion_client = GermanBankNotionClient(token)

    if online:
        if not token:
            click.abort("Missing token")

        nouns = notion_client.get_bank_nouns()
        verbs = [
            verb
            for verb in notion_client.get_bank_verbs()
            if all([
                verb.conj_ich_1ps,
                verb.conj_du_2ps,
                verb.conj_er_3ps,
                verb.conj_wir_1pp,
                verb.conj_ihr_2pp,
                verb.conj_sie_3pp,
            ]) and 'generate' in verb.tags
        ]
    else:
        nouns = BANK_NOUNS
        verbs = BANK_VERBS

    deck = genanki.Deck(
        deck_id=1878326705,  # Hard-coded value selected by me
        name="German::Grammar",
    )

    added_count = 0

    basic_sentence = BasicSentence.make_random(nouns, verbs)

    # TODO: sometimes add an adjective?
    # TODO: make questions?
    while True:
        note = basic_sentence.to_anki_note()

        print(f"{note.fields[1]} ({note.fields[3]})")
        print(note.fields[0])
        print()

        try:
            response = input("Add? [y/R/n]")
        except KeyboardInterrupt:
            click.echo("Exiting!")
            click.echo("")
            break

        def _rotate(basic_sentence: BasicSentence) -> BasicSentence:
            try:
                res = basic_sentence.rotate()
                click.echo("Rotated!")
                click.echo("")
            except StopIteration:
                res = basic_sentence.first()
                click.echo("Rotated! (back to beginning!)")
                click.echo("")
            except MissingGermanPluralWord:
                res = BasicSentence.make_random(nouns, verbs)
                click.echo("No plural! New word!")
                click.echo("")
            
            return res

        if response == 'y':
            deck.add_note(note)
            added_count += 1
            click.echo("Added!")
            click.echo("")
            basic_sentence = _rotate(basic_sentence)
        elif response == 'r' or response == '':
            basic_sentence = _rotate(basic_sentence)
        elif response == 'n':
            basic_sentence = BasicSentence.make_random(nouns, verbs)
            click.echo("New sentence!")
            click.echo("")

    if added_count:
        genanki.Package([deck]).write_to_file(output_filename)
        click.echo(f"Complete! Added {added_count} cards. Now import {output_filename} to Anki, fix any changes, and sync Anki to AnkiCloud.")


if __name__ == "__main__":
    cli_group.add_command(play)
    cli_group()
