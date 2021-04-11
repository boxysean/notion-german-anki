from sean_learns_german.constants import GermanCase, NounGender
from sean_learns_german.models.german_models import BankNoun, Verb


BANK_NOUNS = [
    BankNoun(
        german_word_singular="Mann",
        german_word_plural="Männer",
        english_word="man",
        gender=NounGender.MASCULINE,
        tags=[],
    ),
    BankNoun(
        german_word_singular="Frau",
        german_word_plural="Frauen",
        english_word="woman",
        gender=NounGender.FEMININE,
        tags=[],
    ),
    BankNoun(
        german_word_singular="Angebot",
        german_word_plural="Angebote",
        english_word="agreement",
        gender=NounGender.NEUTER,
        tags=[],
    ),
]

BANK_VERBS = [
    Verb(
        german_word="haben",
        english_word="to have",
        requires_case=GermanCase.ACCUSATIVE,
        conj_ich_1ps="habe",
        conj_du_2ps="habst",
        conj_er_3ps="hat",
        conj_wir_1pp="haben",
        conj_ihr_2pp="habt",
        conj_sie_3pp="haben",
        tags=[],
    ),
    Verb(
        german_word="sehen",
        english_word="to see",
        requires_case=GermanCase.ACCUSATIVE,
        conj_ich_1ps="sehe",
        conj_du_2ps="siehst",
        conj_er_3ps="sieht",
        conj_wir_1pp="sehen",
        conj_ihr_2pp="seht",
        conj_sie_3pp="sehen",
        tags=[],
    ),
    Verb(
        german_word="sein",
        english_word="to be",
        requires_case=GermanCase.NOMINATIVE,
        conj_ich_1ps="bin",
        conj_du_2ps="bist",
        conj_er_3ps="ist",
        conj_wir_1pp="sind",
        conj_ihr_2pp="seid",
        conj_sie_3pp="sind",
        tags=[],
    ),
]
