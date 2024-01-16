from enum import Enum, unique

@unique
class AudioSource(Enum):
    ORIGINAL = 'Eredeti hangfájl'
    PREVIEWTEXT = 'Előnézet szöveg'
    SPLITLIST = 'Vágatlan szegmensek'
    TRIMLIST = 'Vágott szegmensek'