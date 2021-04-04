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
    FIRST_PERSON_SINGULAR = "first-person singular"
    SECOND_PERSON_SINGULAR = "second-person singular"
    THIRD_PERSON_SINGULAR = "third-person singular"
    FIRST_PERSON_PLURAL = "first-person plural"
    SECOND_PERSON_PLURAL = "second-person plural"
    THIRD_PERSON_PLURAL = "third-person plural"


class GermanCase(str, enum.Enum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"


class ArticleType(str, enum.Enum):
    DEFINITE = "definite"
    INDEFINITE = "indefinite"


class PronounType(str, enum.Enum):
    PERSONAL = "personal"
    POSSESSIVE = "possessive"


class Cardinality(str, enum.Enum):
    SINGULAR = 'singular'
    PLURAL = 'plural'
