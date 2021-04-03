import enum


class BankCategory(str, enum.Enum):
    VOCABULARY = "Vocabulary"
    PHRASE = "Phrase"


class PartsOfSpeech(str, enum.Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    CONJUNCTION = "conjunction"
    NUMBER = "number"


class GermanCases(str, enum.Enum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
