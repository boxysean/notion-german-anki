import enum


class BankCategory(str, enum.Enum):
    VOCABULARY = "Vocabulary"
    PHRASE = "Phrase"


class NounGender(str, enum.Enum):
    MASCULINE = 'der'
    FEMININE = 'die'
    NEUTER = 'das'


class PartsOfSpeech(str, enum.Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    CONJUNCTION = "conjunction"
    NUMBER = "number"


class SpeechPerspective(str, enum.Enum):
    FIRST_PERSON = "first-person"
    SECOND_PERSON = "second-person"
    THIRD_PERSON = "third-person"


class GermanCase(str, enum.Enum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    DATIVE = "dative"
    GENITIVE = "genitive"


class ArticleType(str, enum.Enum):
    DEFINITE = "definite"
    INDEFINITE = "indefinite"


class PronounType(str, enum.Enum):
    PERSONAL = "personal"
    POSSESSIVE = "possessive"


class Cardinality(str, enum.Enum):
    SINGULAR = 'singular'
    PLURAL = 'plural'
