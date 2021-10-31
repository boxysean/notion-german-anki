import dataclasses
import logging
import random
import typing

import enforce_typing

from sean_learns_german.constants import ArticleType, Cardinality, GermanCase, NounGender, PronounType, SpeechPerspective, PartsOfSpeech
from sean_learns_german.errors import MissingGender, MissingGermanPluralWord


@dataclasses.dataclass
class Phrase:
    german: str
    english: str
    tags: typing.List[str]


@dataclasses.dataclass
class BankWord:
    tags: typing.List[str]


@dataclasses.dataclass
class BankVocabulary(BankWord):
    german: str
    english_word: str
    english_synonyms: str
    part_of_speech: PartsOfSpeech


@enforce_typing.enforce_types
@dataclasses.dataclass
class BankNoun(BankWord):
    german_word_singular: str
    german_word_plural: typing.Optional[str]
    english_word: str
    english_synonyms: str
    gender: NounGender

    def __post_init__(self):
        if not self.gender:
            raise MissingGender()

    def random_noun(self) -> 'Noun':
        random_article_type = random.choice([article_type for article_type in list(ArticleType)])

        return Noun(
            article_type=random_article_type,
            german_word_singular=self.german_word_singular,
            german_word_plural=self.german_word_plural,
            english_word=self.english_word,
            english_synonyms=self.english_synonyms,
            gender=self.gender,
            perspective=SpeechPerspective.THIRD_PERSON,
            cardinality=Cardinality.SINGULAR,
            tags=self.tags,
        )

    def __lt__(self, o):
        return self.german_word_singular < o.german_word_singular



@dataclasses.dataclass
class Noun(BankNoun):
    article_type: ArticleType
    perspective: SpeechPerspective
    cardinality: Cardinality

    def __post_init__(self):
        super().__post_init__()
        if self.cardinality == Cardinality.PLURAL and not self.german_word_plural:
            raise MissingGermanPluralWord(self.german_word_singular)

    def first(self) -> 'Noun':
        return Noun(
            german_word_singular=self.german_word_singular,
            german_word_plural=self.german_word_plural,
            english_word=self.english_word,
            english_synonyms=self.english_synonyms,
            gender=self.gender,
            article_type=self.article_type.first(),
            perspective=self.perspective,
            cardinality=self.cardinality.first(),
            tags=self.tags,
        )

    def rotate(self) -> 'Noun':
        # Rotate: article_type, cardinality
        rotated_cardinality = self.cardinality

        try:
            rotated_article_type = self.article_type.next()
        except StopIteration:
            rotated_article_type = self.article_type.first()
            try:
                rotated_cardinality = self.cardinality.next()
            except StopIteration:
                raise

        try:
            return Noun(
                german_word_singular=self.german_word_singular,
                german_word_plural=self.german_word_plural,
                english_word=self.english_word,
                english_synonyms=self.english_synonyms,
                gender=self.gender,
                article_type=rotated_article_type,
                perspective=self.perspective,
                cardinality=rotated_cardinality,
                tags=self.tags,
            )
        except MissingGermanPluralWord as e:
            raise StopIteration() from e

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
class Pronoun:
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


@enforce_typing.enforce_types
@dataclasses.dataclass
class Verb(BankWord):
    german_word: str
    english_word: str
    english_synonyms: typing.Optional[str]
    conj_ich_1ps: str
    conj_du_2ps: str
    conj_er_3ps: str
    conj_wir_1pp: str
    conj_ihr_2pp: str
    conj_sie_3pp: str
    requires_case: typing.Optional[GermanCase]

    def __post_init__(self):
        if self.requires_case is None:
            logging.info("Verb %s is missing requires_case, assuming accusative", self.german_word)
            self.requires_case = GermanCase.ACCUSATIVE
        
        if not all([
            self.conj_ich_1ps,
            self.conj_du_2ps,
            self.conj_er_3ps,
            self.conj_wir_1pp,
            self.conj_ihr_2pp,
            self.conj_sie_3pp,
        ]):
            logging.warning("Verb %s is not fully conjugated", self.german_word)

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

    def make_english_str(self) -> str:
        return self.english_word

    def __lt__(self, o):
        return self.german_word < o.german_word
