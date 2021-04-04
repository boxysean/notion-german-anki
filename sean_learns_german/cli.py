import dataclasses
import enum
import logging
import random
import typing

import click
import genanki
import notion.client
import notion.collection


from sean_learns_german.models import GermanBankItem, GermanBankVocabulary, GermanBankNoun, GermanBankVerb, GermanBankPhrase
from sean_learns_german.genanki_models import GermanNote
from sean_learns_german.constants import BankCategory, PartsOfSpeech, GermanCase, SpeechPerspective, ArticleType, NounGender, PronounType, Cardinality
from sean_learns_german.errors import MissingGender, MissingPartOfSpeech


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

    class ArticledNounOrPronoun:
        @classmethod
        def random(cls) -> 'ArticledNounOrPronoun':
            pass

    @dataclasses.dataclass
    class ArticledNoun(ArticledNounOrPronoun):
        noun: GermanBankNoun
        article_type: ArticleType
        perspective: SpeechPerspective
        cardinality: Cardinality

        @classmethod
        def random(cls, nouns: typing.List[GermanBankNoun]) -> 'ArticledNoun':
            random_article_type = random.choice([article_type.value for article_type in list(ArticleType)])
            random_noun = random.choice(nouns)

            return cls(
                article_type=random_article_type,
                noun=random_noun,
                perspective=SpeechPerspective.THIRD_PERSON_SINGULAR,
                cardinality=Cardinality.SINGULAR,
            )
        
        def get_article(self, case: GermanCase) -> str:
            if self.article_type == ArticleType.DEFINITE:
                if self.noun.gender == NounGender.MASCULINE:
                    if case == GermanCase.NOMINATIVE:
                        return 'der'
                    elif case == GermanCase.ACCUSATIVE:
                        return 'den'
                elif self.noun.gender == NounGender.FEMININE:
                    return 'die'
                elif self.noun.gender == NounGender.NEUTER:
                    return 'das'
            elif self.article_type == ArticleType.INDEFINITE:
                if self.noun.gender == NounGender.MASCULINE:
                    if case == GermanCase.NOMINATIVE:
                        return 'ein'
                    elif case == GermanCase.ACCUSATIVE:
                        return 'einen'
                elif self.noun.gender == NounGender.FEMININE:
                    return 'eine'
                elif self.noun.gender == NounGender.NEUTER:
                    return 'ein'
            raise ValueError(f"Unexpected article type, gender, and/or case: {self.article_type}, {self.noun.gender}, {case}")

        def make_str(self, case: GermanCase) -> str:
            return f"{self.get_article(case)} {self.noun.german}"

        def blank_it(self, case: GermanCase) -> str:
            return f"({self.noun.german}, {self.article_type} {self.cardinality})"

    @dataclasses.dataclass
    class Pronoun(ArticledNounOrPronoun):
        pronoun_type: PronounType
        perspective: SpeechPerspective
        gender: typing.Optional[NounGender]
        cardinality: Cardinality

        @classmethod
        def random(cls) -> 'Pronoun':
            random_perspective = random.choice([perspective.value for perspective in list(SpeechPerspective)])

            if random_perspective == SpeechPerspective.THIRD_PERSON_SINGULAR:
                random_gender_or_none = random.choice([gender.value for gender in list(NounGender)])
            else:
                random_gender_or_none = None

            return cls(
                pronoun_type=PronounType.PERSONAL,
                perspective=random_perspective,
                gender=random_gender_or_none,
                cardinality=Cardinality.PLURAL if random_perspective in [SpeechPerspective.FIRST_PERSON_PLURAL, SpeechPerspective.SECOND_PERSON_PLURAL, SpeechPerspective.THIRD_PERSON_PLURAL] else Cardinality.SINGULAR,
            )

        def get_pronoun(self) -> str:
            # https://deutsch.lingolia.com/en/grammar/declension/nominative
            if self.pronoun_type == PronounType.PERSONAL:
                if self.perspective == SpeechPerspective.FIRST_PERSON_SINGULAR:
                    return 'ich'
                elif self.perspective == SpeechPerspective.SECOND_PERSON_SINGULAR:
                    return 'du'
                elif self.perspective == SpeechPerspective.THIRD_PERSON_SINGULAR:
                    if self.gender == NounGender.MASCULINE:
                        return 'er'
                    elif self.gender == NounGender.FEMININE:
                        return 'sie'
                    elif self.gender == NounGender.NEUTER:
                        return 'es'
                elif self.perspective == SpeechPerspective.FIRST_PERSON_PLURAL:
                    return 'wir'
                elif self.perspective == SpeechPerspective.SECOND_PERSON_PLURAL:
                    return 'ihr'
                elif self.perspective == SpeechPerspective.THIRD_PERSON_PLURAL:
                    return 'Sie'
            elif self.pronoun_type == PronounType.POSSESSIVE:
                if self.perspective == SpeechPerspective.FIRST_PERSON_SINGULAR:
                    if self.gender == NounGender.FEMININE or plural:
                        return 'meine'
                    elif self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                        return 'mein'
                elif self.perspective == SpeechPerspective.SECOND_PERSON_SINGULAR:
                    if self.gender == NounGender.FEMININE or plural:
                        return 'deine'
                    elif self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                        return 'dein'
                elif self.perspective == SpeechPerspective.SECOND_PERSON_SINGULAR:
                    if self.gender == NounGender.FEMININE:
                        return 'deine'
                    if self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                        return 'dein'
                # TODO: incomplete?
            raise ValueError(f"Unexpected pronoun type, perspective, and/or gender: {self.pronoun_type}, {self.perspective}, {self.gender}")

        def make_str(self, case: GermanCase) -> str:
            del case
            return f"{self.get_pronoun()}"

        def blank_it(self, case: GermanCase) -> str:
            del case
            if self.perspective == SpeechPerspective.THIRD_PERSON_SINGULAR:
                return f"({self.gender})"
            else:
                return f"({self.perspective})"

    def generate_sentence(nouns: typing.List[GermanBankNoun], verbs: typing.List[GermanBankVerb]) -> str:
        # https://iwillteachyoualanguage.com/learn/german/german-tips/german-cases-explained
        subject_is_pronoun = random.choice([False, True])

        if subject_is_pronoun:
            subject = Pronoun.random()
        else:
            subject = ArticledNoun.random(nouns=nouns)

        random_verb = random.choice(verbs)
        object_ = ArticledNoun.random(nouns=nouns)

        answer_sentence = (
            f"{subject.make_str(case=GermanCase.NOMINATIVE)} "
            f"{random_verb.conjugate(subject.perspective)} "
            f"{object_.make_str(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)}"
        )

        blank_it = random.choice(['subject', 'verb', 'object'])

        # blank_it = 'subject'

        if blank_it == 'subject':
            question_sentence = (
                "____ "
                f"{random_verb.conjugate(subject.perspective)} "
                f"{object_.make_str(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)} "
                f"{subject.blank_it(case=GermanCase.NOMINATIVE)}"
            )
        elif blank_it == 'verb':
            question_sentence = (
                f"{subject.make_str(case=GermanCase.NOMINATIVE)} "
                "____ "
                f"{object_.make_str(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)} "
                f"({random_verb.german})"
            )
        elif blank_it == 'object':
            question_sentence = (
                f"{subject.make_str(case=GermanCase.NOMINATIVE)} "
                f"{random_verb.conjugate(subject.perspective)} "
                f"____ "
                f"{object_.blank_it(case=GermanCase.ACCUSATIVE if random_verb.requires_accusative else GermanCase.NOMINATIVE)}"
            )

        # return question_sentence
        return question_sentence[0].upper() + question_sentence[1:] + ' '

    NOUNS = [
        GermanBankNoun.make(
            category="Vocabulary",
            german="Mann",
            plural="Männer",
            english="man",
            part_of_speech=PartsOfSpeech.NOUN,
            gender=NounGender.MASCULINE,
        ),
        GermanBankNoun.make(
            category="Vocabulary",
            german="Frau",
            plural="Frauen",
            english="woman",
            part_of_speech=PartsOfSpeech.NOUN,
            gender=NounGender.FEMININE,
        ),
        GermanBankNoun.make(
            category="Vocabulary",
            german="Angebot",
            plural="Angebote",
            english="agreement",
            part_of_speech=PartsOfSpeech.NOUN,
            gender=NounGender.NEUTER,
        ),
    ]

    VERBS = [
        GermanBankVerb.make(
            category="Vocabulary",
            german="haben",
            english="to have",
            part_of_speech=PartsOfSpeech.VERB,
            requires_accusative=True,
            conj_ich_1ps="habe",
            conj_du_2ps="habst",
            conj_er_3ps="hat",
            conj_wir_1pp="haben",
            conj_ihr_2pp="habt",
            conj_sie_3pp="haben",
        ),
        GermanBankVerb.make(
            category="Vocabulary",
            german="sehen",
            english="to see",
            part_of_speech=PartsOfSpeech.VERB,
            requires_accusative=True,
            conj_ich_1ps="sehe",
            conj_du_2ps="siehst",
            conj_er_3ps="sieht",
            conj_wir_1pp="sehen",
            conj_ihr_2pp="seht",
            conj_sie_3pp="sehen",
        ),
        GermanBankVerb.make(
            category="Vocabulary",
            german="sein",
            english="to be",
            part_of_speech=PartsOfSpeech.VERB,
            requires_accusative=False,
            conj_ich_1ps="bin",
            conj_du_2ps="bist",
            conj_er_3ps="ist",
            conj_wir_1pp="sind",
            conj_ihr_2pp="seid",
            conj_sie_3pp="sind",
        ),
    ]


    # TODO: sometimes add an adjective?
    # TODO: make questions?
    for i in range(25):
        print(generate_sentence(NOUNS, VERBS))


if __name__ == "__main__":
    cli_group()
