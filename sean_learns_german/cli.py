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
from sean_learns_german.errors import MissingCategory, MissingGender, MissingPartOfSpeech
from sean_learns_german.models.notion_models import GermanBankItem, GermanBankVocabulary, GermanBankNoun, GermanBankVerb, GermanBankPhrase, BANK_NOUNS, BANK_VERBS
from sean_learns_german.models.genanki_models import GermanNote, GENANKI_GRAMMAR_MODEL
from sean_learns_german.models.german_models import ArticledNounOrPronoun, ArticledNoun, Pronoun, Verb


logging.basicConfig(
    level=logging.INFO,
)


NOTION_GERMAN_BANK_VIEW_URL = "https://www.notion.so/0bf4b6fd23af40dba8d4c23206b2f1e3?v=e2f51d7caf4a43c7a791304984f019bb"


@click.group()
def cli_group():
    pass


def _load_bank_items_from_notion(token: str) -> typing.Generator[GermanBankItem, None, None]:
    client = notion.client.NotionClient(token_v2=token)
    view = client.get_collection_view(NOTION_GERMAN_BANK_VIEW_URL)

    for row in view.collection.get_rows():
        try:
            german_bank_item = GermanBankItem.from_notion_row(row)
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


@cli_group.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
@click.option("--output-filename", type=str, default="output.apkg")
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

    for german_bank_item in _load_bank_items_from_notion(token):
        german_note = german_bank_item.to_german_note()
        decks[german_bank_item.category].add_note(german_note)

    genanki.Package(decks.values()).write_to_file(output_filename)
    click.echo(f"Complete! Now import {output_filename} to Anki, fix any changes, and sync Anki to AnkiCloud.")


@cli_group.command()
@click.option("--token", type=str, help="Get from token_v2 value stored in www.notion.so cookies. Link: chrome://settings/cookies/detail?site=www.notion.so", required=True,)
@click.option("--output-filename", type=str, default="grammar_output.apkg")
def generate_sentences(token: str, output_filename: str):
    """
    Generates sentences
    """


    @dataclasses.dataclass
    class BasicSentence:
        subject: ArticledNounOrPronoun
        verb: Verb
        object_: ArticledNoun

        @classmethod
        def make_random(cls, nouns: typing.List[GermanBankNoun], verbs: typing.List[GermanBankVerb]) -> 'BasicSentence':
            # https://iwillteachyoualanguage.com/learn/german/german-tips/german-cases-explained
            subject_is_pronoun = random.choice([False, True])

            if subject_is_pronoun:
                subject = Pronoun.random()
            else:
                subject = ArticledNoun.random(nouns=nouns)

            return cls(
                subject=subject,
                verb=Verb.random(verbs=verbs),
                object_=ArticledNoun.random(nouns=nouns),
            )
        
        def first(self) -> 'BasicSentence':
            return BasicSentence(
                subject=self.subject.first(),
                verb=self.verb,
                object_=self.object_.first(),
            )

        def rotate(self) -> 'BasicSentence':
            rotated_object = self.object_

            try:
                rotated_subject = self.subject.rotate()
            except StopIteration:
                rotated_subject = self.subject.first()
                try:
                    rotated_object = self.object_.rotate()
                except:
                    raise

            return BasicSentence(
                subject=rotated_subject,
                verb=self.verb,
                object_=rotated_object,
            )

        def to_anki_note(self) -> GermanNote:
            answer_sentence = (
                f"{self.subject.make_str(case=GermanCase.NOMINATIVE)} "
                f"{self.verb.conjugate(self.subject.perspective, self.subject.cardinality)} "
                f"{self.object_.make_str(case=self.verb.requires_case)}"
            )

            english_answer_sentence = (
                f"{self.subject.make_english_str()} + "
                f"{self.verb.make_english_str()} + "
                f"{self.object_.make_english_str()}"
            )

            blank_it = random.choice(['subject', 'verb', 'object'])

            if blank_it == 'subject':
                question_sentence = (
                    "____ "
                    f"{self.verb.conjugate(self.subject.perspective, self.subject.cardinality)} "
                    f"{self.object_.make_str(case=self.verb.requires_case)}"
                )
                hint = self.subject.make_hint(case=GermanCase.NOMINATIVE)
            elif blank_it == 'verb':
                question_sentence = (
                    f"{self.subject.make_str(case=GermanCase.NOMINATIVE)} "
                    "____ "
                    f"{self.object_.make_str(case=self.verb.requires_case)}"
                )
                hint = self.verb.german_word
            elif blank_it == 'object':
                question_sentence = (
                    f"{self.subject.make_str(case=GermanCase.NOMINATIVE)} "
                    f"{self.verb.conjugate(self.subject.perspective, self.subject.cardinality)} "
                    f"____"
                )
                hint = self.object_.make_hint(case=self.verb.requires_case)

            def _sentence_format(s: str) -> str:
                return s[0].upper() + s[1:]

            return GermanNote(
                model=GENANKI_GRAMMAR_MODEL,
                fields=[
                    _sentence_format(answer_sentence),
                    _sentence_format(question_sentence),
                    english_answer_sentence,
                    hint if hint is not None else "",
                    "ArticledNounOrPronoun+Verb+Noun",
                ],
                tags=["ArticledNounOrPronoun+Verb+Noun",],
            )


    nouns = []
    verbs = []

    for german_bank_item in _load_bank_items_from_notion(token):
        if german_bank_item.category == BankCategory.VOCABULARY:
            if german_bank_item.part_of_speech == PartsOfSpeech.NOUN:
                nouns.append(german_bank_item)
            elif german_bank_item.part_of_speech == PartsOfSpeech.VERB:
                if all([
                    german_bank_item.conj_ich_1ps,
                    german_bank_item.conj_du_2ps,
                    german_bank_item.conj_er_3ps,
                    german_bank_item.conj_wir_1pp,
                    german_bank_item.conj_ihr_2pp,
                    german_bank_item.conj_sie_3pp,
                ]) and 'generate' in german_bank_item.tags:
                    verbs.append(german_bank_item)

    deck = genanki.Deck(
        deck_id=1878326705,  # Hard-coded value selected by me
        name="German::Grammar",
    )

    notes = []
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
            response = input("Add? [y/R/s]")
        except KeyboardInterrupt:
            click.echo("Exiting!")
            click.echo("")
            break

        if response == 'y':
            deck.add_note(note)
            added_count += 1
            click.echo("Added!")
            click.echo("")
            try:
                basic_sentence = basic_sentence.rotate()
            except StopIteration:
                basic_sentence = basic_sentence.first()
                click.echo("Rotated! (back to beginning!)")
                click.echo("")
            else:
                click.echo("Rotated!")
                click.echo("")
        elif response == 'r' or response == '':
            try:
                basic_sentence = basic_sentence.rotate()
            except StopIteration:
                basic_sentence = basic_sentence.first()
                click.echo("Rotated! (back to beginning!)")
                click.echo("")
            else:
                click.echo("Rotated!")
                click.echo("")
        elif response == 's':
            basic_sentence = BasicSentence.make_random(nouns, verbs)
            click.echo("New sentence!")
            click.echo("")

    if added_count:
        genanki.Package([deck]).write_to_file(output_filename)
        click.echo(f"Complete! Added {added_count} cards. Now import {output_filename} to Anki, fix any changes, and sync Anki to AnkiCloud.")


if __name__ == "__main__":
    cli_group()
