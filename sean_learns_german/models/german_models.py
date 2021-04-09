import dataclasses
import random
import typing

from sean_learns_german.constants import ArticleType, Cardinality, GermanCase, NounGender, PronounType, SpeechPerspective
from sean_learns_german.errors import MissingGermanPluralWord
from sean_learns_german.models.genanki_models import GermanNote, GENANKI_GRAMMAR_MODEL
from sean_learns_german.models.notion_models import GermanBankNoun, GermanBankVerb


class ArticledNounOrPronoun:
    # TODO: Intended as a protocol
    pass


@dataclasses.dataclass
class ArticledNoun(ArticledNounOrPronoun):
    german_word_singular: str
    german_word_plural: str
    english_word: str
    gender: NounGender
    article_type: ArticleType
    perspective: SpeechPerspective
    cardinality: Cardinality

    def __post_init__(self):
        if self.cardinality == Cardinality.PLURAL and not self.german_word_plural:
            raise MissingGermanPluralWord(self.german_word_singular)

    @classmethod
    def random(cls, nouns: typing.List[GermanBankNoun]) -> 'ArticledNoun':
        random_article_type = random.choice([article_type for article_type in list(ArticleType)])
        random_noun = random.choice(nouns)

        return cls(
            article_type=random_article_type,
            german_word_singular=random_noun.german,
            german_word_plural=random_noun.german_plural,
            english_word=random_noun.english,
            gender=random_noun.gender,
            perspective=SpeechPerspective.THIRD_PERSON,
            cardinality=Cardinality.SINGULAR,
        )
    
    def first(self) -> 'ArticledNoun':
        return ArticledNoun(
            german_word_singular=self.german_word_singular,
            german_word_plural=self.german_word_plural,
            english_word=self.english_word,
            gender=self.gender,
            article_type=self.article_type.first(),
            perspective=self.perspective,
            cardinality=self.cardinality.first(),
        )

    def rotate(self) -> 'ArticledNoun':
        # Rotate: article_type, cardinality
        rotated_cardinality = self.cardinality

        try:
            rotated_article_type = self.article_type.next()
        except StopIteration:
            rotated_article_type = self.article_type.first()
            try:
                rotated_cardinality = self.cardinality.next()
            except StopIteration:
                rotated_cardinality = self.cardinality.first()
                raise

        return ArticledNoun(
            german_word_singular=self.german_word_singular,
            german_word_plural=self.german_word_plural,
            english_word=self.english_word,
            gender=self.gender,
            article_type=rotated_article_type,
            perspective=self.perspective,
            cardinality=rotated_cardinality,
        )

    def get_article(self, case: GermanCase) -> typing.Optional[str]:
        if self.cardinality == Cardinality.PLURAL:
            if case == GermanCase.NOMINATIVE or case == GermanCase.ACCUSATIVE:
                if self.article_type == ArticleType.DEFINITE:
                    return 'die'
                elif self.article_type == ArticleType.INDEFINITE:
                    return None
        elif self.cardinality == Cardinality.SINGULAR:
            if self.article_type == ArticleType.DEFINITE:
                if self.gender == NounGender.MASCULINE:
                    if case == GermanCase.NOMINATIVE:
                        return 'der'
                    elif case == GermanCase.ACCUSATIVE:
                        return 'den'
                elif self.gender == NounGender.FEMININE:
                    return 'die'
                elif self.gender == NounGender.NEUTER:
                    return 'das'
            elif self.article_type == ArticleType.INDEFINITE:
                if self.gender == NounGender.MASCULINE:
                    if case == GermanCase.NOMINATIVE:
                        return 'ein'
                    elif case == GermanCase.ACCUSATIVE:
                        return 'einen'
                elif self.gender == NounGender.FEMININE:
                    return 'eine'
                elif self.gender == NounGender.NEUTER:
                    return 'ein'
        raise ValueError(f"Unexpected article type, gender, case, and/or cardinality: {self.article_type}, {self.gender}, {case}, {self.cardinality}")

    def make_str(self, case: GermanCase) -> str:
        article = self.get_article(case)
        
        if self.cardinality == Cardinality.SINGULAR:
            word = self.german_word_singular
        elif self.cardinality == Cardinality.PLURAL:
            word = self.german_word_plural

        if article:
            return f"{article} {word}"
        else:
            return word

    def make_english_str(self) -> str:
        return ("the" if self.article_type == ArticleType.DEFINITE else "a") + " " + self.english_word

    def make_hint(self, case: GermanCase) -> typing.Optional[str]:
        return f"{self.english_word}, {self.article_type} {self.cardinality}"


@dataclasses.dataclass
class Pronoun(ArticledNounOrPronoun):
    pronoun_type: PronounType
    perspective: SpeechPerspective
    gender: typing.Optional[NounGender]
    cardinality: Cardinality

    def __post_init__(self):
        if self.gender is None and self.perspective == SpeechPerspective.THIRD_PERSON and self.cardinality == Cardinality.SINGULAR:
            raise ValueError("Gender cannot be None with a third-person singular pronoun")

    @classmethod
    def random(cls) -> 'Pronoun':
        random_perspective = random.choice([perspective for perspective in list(SpeechPerspective)])
        random_cardinality = random.choice([cardinality for cardinality in list(Cardinality)])

        if random_perspective == SpeechPerspective.THIRD_PERSON and random_cardinality == Cardinality.SINGULAR:
            random_gender_or_none = random.choice([gender for gender in list(NounGender)])
        else:
            random_gender_or_none = None

        return cls(
            pronoun_type=PronounType.PERSONAL,
            perspective=random_perspective,
            gender=random_gender_or_none,
            cardinality=random_cardinality,
        )

    def first(self) -> 'Pronoun':
        return Pronoun(
            perspective=self.perspective.first(),
            cardinality=self.cardinality.first(),
            pronoun_type=self.pronoun_type.first(),
            gender=self.gender,
        )

    def rotate(self) -> 'Pronoun':
        rotated_cardinality = self.cardinality
        rotated_pronoun_type = self.pronoun_type

        try:
            rotated_speech_perspective = self.perspective.next()
        except StopIteration:
            rotated_speech_perspective = self.perspective.first()
            try:
                rotated_cardinality = self.cardinality.next()
            except StopIteration:
                rotated_cardinality = self.cardinality.first()
                raise
                # try:
                #     rotated_pronoun_type = self.pronoun_type.next()
                # except StopIteration:
                #     rotated_pronoun_type = self.pronoun_type.first()
                #     raise

        if rotated_speech_perspective == SpeechPerspective.THIRD_PERSON and rotated_cardinality == Cardinality.SINGULAR:
            rotated_gender = random.choice([noun_gender for noun_gender in list(NounGender)])
        else:
            rotated_gender = None

        return Pronoun(
            perspective=rotated_speech_perspective,
            cardinality=rotated_cardinality,
            pronoun_type=rotated_pronoun_type,
            gender=rotated_gender,
        )

    def get_pronoun(self) -> str:
        # https://deutsch.lingolia.com/en/grammar/declension/nominative
        if self.pronoun_type == PronounType.PERSONAL:
            if self.perspective == SpeechPerspective.FIRST_PERSON and self.cardinality == Cardinality.SINGULAR:
                return 'ich'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.SINGULAR:
                return 'du'
            elif self.perspective == SpeechPerspective.THIRD_PERSON and self.cardinality == Cardinality.SINGULAR:
                if self.gender == NounGender.MASCULINE:
                    return 'er'
                elif self.gender == NounGender.FEMININE:
                    return 'sie'
                elif self.gender == NounGender.NEUTER:
                    return 'es'
            elif self.perspective == SpeechPerspective.FIRST_PERSON and self.cardinality == Cardinality.PLURAL:
                return 'wir'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.PLURAL:
                return 'ihr'
            elif self.perspective == SpeechPerspective.THIRD_PERSON and self.cardinality == Cardinality.PLURAL:
                return 'Sie'
        elif self.pronoun_type == PronounType.POSSESSIVE:
            if self.perspective == SpeechPerspective.FIRST_PERSON and self.cardinality == Cardinality.SINGULAR:
                if self.gender == NounGender.FEMININE:
                    return 'meine'
                elif self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                    return 'mein'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.SINGULAR:
                if self.gender == NounGender.FEMININE:
                    return 'deine'
                elif self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                    return 'dein'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.SINGULAR:
                if self.gender == NounGender.FEMININE:
                    return 'deine'
                if self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                    return 'dein'
            # TODO: incomplete?
        raise ValueError(f"Unexpected pronoun type, perspective, and/or gender: {self.pronoun_type}, {self.perspective}, {self.gender}")

    def make_str(self, case: GermanCase) -> str:
        del case
        return f"{self.get_pronoun()}"

    def make_english_str(self) -> str:
        if self.pronoun_type == PronounType.PERSONAL:
            if self.perspective == SpeechPerspective.FIRST_PERSON and self.cardinality == Cardinality.SINGULAR:
                return 'I'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.SINGULAR:
                return 'you'
            elif self.perspective == SpeechPerspective.THIRD_PERSON and self.cardinality == Cardinality.SINGULAR:
                if self.gender == NounGender.MASCULINE:
                    return 'he'
                elif self.gender == NounGender.FEMININE:
                    return 'she'
                elif self.gender == NounGender.NEUTER:
                    return 'it'
            elif self.perspective == SpeechPerspective.FIRST_PERSON and self.cardinality == Cardinality.PLURAL:
                return 'we'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.PLURAL:
                return 'you'
            elif self.perspective == SpeechPerspective.THIRD_PERSON and self.cardinality == Cardinality.PLURAL:
                return 'they'
        raise ValueError()

    def make_hint(self, case: GermanCase) -> typing.Optional[str]:
        del case
        if self.perspective == SpeechPerspective.THIRD_PERSON and self.cardinality == Cardinality.SINGULAR:
            return f"{self.gender}"
        else:
            return None


@dataclasses.dataclass
class Verb:
    german_word: str
    english_word: str
    conj_ich_1ps: str
    conj_du_2ps: str
    conj_er_3ps: str
    conj_wir_1pp: str
    conj_ihr_2pp: str
    conj_sie_3pp: str
    requires_case: GermanCase

    def conjugate(self, perspective: SpeechPerspective, cardinality: Cardinality):
        if perspective == SpeechPerspective.FIRST_PERSON and cardinality == Cardinality.SINGULAR:
            return self.conj_ich_1ps
        elif perspective == SpeechPerspective.SECOND_PERSON and cardinality == Cardinality.SINGULAR:
            return self.conj_du_2ps
        elif perspective == SpeechPerspective.THIRD_PERSON and cardinality == Cardinality.SINGULAR:
            return self.conj_er_3ps
        elif perspective == SpeechPerspective.FIRST_PERSON and cardinality == Cardinality.PLURAL:
            return self.conj_wir_1pp
        elif perspective == SpeechPerspective.SECOND_PERSON and cardinality == Cardinality.PLURAL:
            return self.conj_ihr_2pp
        elif perspective == SpeechPerspective.THIRD_PERSON and cardinality == Cardinality.PLURAL:
            return self.conj_sie_3pp
        else:
            raise ValueError(perspective)

    @classmethod
    def random(cls, verbs: typing.List[GermanBankVerb]) -> 'Verb':
        random_verb = random.choice(verbs)

        return cls(
            german_word=random_verb.german,
            english_word=random_verb.english,
            conj_ich_1ps=random_verb.conj_ich_1ps,
            conj_du_2ps=random_verb.conj_du_2ps,
            conj_er_3ps=random_verb.conj_er_3ps,
            conj_wir_1pp=random_verb.conj_wir_1pp,
            conj_ihr_2pp=random_verb.conj_ihr_2pp,
            conj_sie_3pp=random_verb.conj_sie_3pp,
            requires_case=random_verb.requires_case,
        )

    def make_english_str(self) -> str:
        return self.english_word


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
                "BasicSentence",
            ],
            tags=["BasicSentence"],
        )
