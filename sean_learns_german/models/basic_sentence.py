import dataclasses
import random
import typing

from sean_learns_german.constants import GermanCase
from sean_learns_german.models.genanki_models import GermanNote, GENANKI_GRAMMAR_MODEL
from sean_learns_german.models.german_models import BankNoun, Verb, Noun, Pronoun, Verb


@dataclasses.dataclass
class BasicSentence:
    subject: typing.Union[Noun, Pronoun]
    verb: Verb
    object_: Noun

    @classmethod
    def make_random(cls, nouns: typing.List[BankNoun], verbs: typing.List[Verb]) -> 'BasicSentence':
        # https://iwillteachyoualanguage.com/learn/german/german-tips/german-cases-explained
        subject_is_pronoun = random.choice([False, True])

        if subject_is_pronoun:
            subject = Pronoun.random()
        else:
            subject = random.choice(nouns).random_noun()

        return cls(
            subject=subject,
            verb=random.choice(verbs),
            object_=random.choice(nouns).random_noun(),
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
                "BasicSentence",
            ],
            tags=["BasicSentence"],
        )
