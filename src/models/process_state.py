from enum import Enum, unique

@unique
class ProcessState(Enum):
    STOPPED = 'stopped'
    SPLITTING = 'Szegmentálás...'
    TRIMMING = 'Trimmelés...'
    GENERATING = 'Generálás...'