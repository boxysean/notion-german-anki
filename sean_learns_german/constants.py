import enum
import typing


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

    @classmethod
    def from_string(cls, s: typing.Optional[str]) -> typing.Optional['NounGender']:
        if s == 'der':
            return cls.MASCULINE
        elif s == 'die':
            return cls.FEMININE
        elif s == 'das':
            return cls.NEUTER
        elif not s:
            return None
        else:
            raise ValueError(f"Unexpected value {s}")


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

    @classmethod
    def from_string(cls, s: typing.Optional[str]) -> typing.Optional['GermanCase']:
        if s == 'nominative':
            return cls.NOMINATIVE
        elif s == 'accusative':
            return cls.ACCUSATIVE
        elif s == 'dative':
            return cls.DATIVE
        elif s == 'genitive':
            return cls.GENITIVE
        elif not s:
            return None
        else:
            raise ValueError(f"Unexpected value {s}")


class ArticleType(str, RotateableEnum):
    DEFINITE = "definite"
    INDEFINITE = "indefinite"


class PronounType(str, RotateableEnum):
    PERSONAL = "personal"
    POSSESSIVE = "possessive"


class Cardinality(str, RotateableEnum):
    SINGULAR = 'singular'
    PLURAL = 'plural'
