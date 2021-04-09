import enum


class RotateableEnum(enum.Enum):
    def next(self):
        members = list(self.__class__)
        index = members.index(self) + 1
        if index >= len(members):
            raise StopIteration('end of enumeration reached')
        return members[index]

    def first(self):
        return list(self.__class__)[0]



class BankCategory(str, enum.Enum):
    VOCABULARY = "Vocabulary"
    PHRASE = "Phrase"


class NounGender(str, RotateableEnum):
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


class SpeechPerspective(str, RotateableEnum):
    FIRST_PERSON = "first-person"
    SECOND_PERSON = "second-person"
    THIRD_PERSON = "third-person"


class GermanCase(str, RotateableEnum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    DATIVE = "dative"
    GENITIVE = "genitive"


class ArticleType(str, RotateableEnum):
    DEFINITE = "definite"
    INDEFINITE = "indefinite"


class PronounType(str, RotateableEnum):
    PERSONAL = "personal"
    POSSESSIVE = "possessive"


class Cardinality(str, RotateableEnum):
    SINGULAR = 'singular'
    PLURAL = 'plural'
