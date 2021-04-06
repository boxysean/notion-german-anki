import dataclasses
import random
import typing

from sean_learns_german.constants import ArticleType, Cardinality, GermanCase, NounGender, PronounType, SpeechPerspective
from sean_learns_german.models.notion_models import GermanBankNoun, GermanBankVerb


class ArticledNounOrPronoun:
    # TODO: Intended as a protocol
    pass


@dataclasses.dataclass
class ArticledNoun(ArticledNounOrPronoun):
    german_word: str
    english_word: str
    gender: NounGender
    article_type: ArticleType
    perspective: SpeechPerspective
    cardinality: Cardinality

    @classmethod
    def random(cls, nouns: typing.List[GermanBankNoun]) -> 'ArticledNoun':
        random_article_type = random.choice([article_type.value for article_type in list(ArticleType)])
        random_noun = random.choice(nouns)

        return cls(
            article_type=random_article_type,
            german_word=random_noun.german,
            english_word=random_noun.english,
            gender=random_noun.gender,
            perspective=SpeechPerspective.THIRD_PERSON,
            cardinality=Cardinality.SINGULAR,
        )
    
    def get_article(self, case: GermanCase) -> str:
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
        raise ValueError(f"Unexpected article type, gender, and/or case: {self.article_type}, {self.gender}, {case}")

    def make_str(self, case: GermanCase) -> str:
        return f"{self.get_article(case)} {self.german_word}"

    def make_english_str(self) -> str:
        return ("the" if self.article_type == ArticleType.DEFINITE else "a") + " " + self.english_word

    def make_hint(self, case: GermanCase) -> typing.Optional[str]:
        return f"{self.german_word}, {self.article_type}"


@dataclasses.dataclass
class Pronoun(ArticledNounOrPronoun):
    pronoun_type: PronounType
    perspective: SpeechPerspective
    gender: typing.Optional[NounGender]
    cardinality: Cardinality

    @classmethod
    def random(cls) -> 'Pronoun':
        random_perspective = random.choice([perspective.value for perspective in list(SpeechPerspective)])
        random_cardinality = random.choice([cardinality.value for cardinality in list(Cardinality)])

        if random_perspective == SpeechPerspective.THIRD_PERSON and random_cardinality == Cardinality.SINGULAR:
            random_gender_or_none = random.choice([gender.value for gender in list(NounGender)])
        else:
            random_gender_or_none = None

        return cls(
            pronoun_type=PronounType.PERSONAL,
            perspective=random_perspective,
            gender=random_gender_or_none,
            cardinality=random_cardinality,
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
                if self.gender == NounGender.FEMININE or plural:
                    return 'meine'
                elif self.gender in [NounGender.MASCULINE, NounGender.NEUTER]:
                    return 'mein'
            elif self.perspective == SpeechPerspective.SECOND_PERSON and self.cardinality == Cardinality.SINGULAR:
                if self.gender == NounGender.FEMININE or plural:
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
