from enum import Enum, unique

@unique
class ProcessState(Enum):
    STOPPED = 'Szünetel'
    SPLITTING = 'Szegmentálás:'
    TRIMMING = 'Trimmelés:'
    GENERATING = 'Generálás:'