import os
from enum import Enum, unique
from utils.general_utils import to_timestamp_sec

@unique
class AudioSource(Enum):
    ORIGINAL = 'Eredeti hangfájl'
    PREVIEWTEXT = 'Előnézet szöveg'
    SPLITLIST = 'Vágatlan szegmensek'
    TRIMLIST = 'Vágott szegmensek'

class AudioFile():
    def __init__(self, segment_number : int, file_path : str, absolute_timestamp : tuple[float, float]) -> None:
        self.segment_number = segment_number
        self.file_path = file_path
        self.absolute_timestamp = absolute_timestamp

    def __str__(self) -> str:
        return f'{os.path.basename(self.file_path)} {to_timestamp_sec(self.absolute_timestamp[0])}-{to_timestamp_sec(self.absolute_timestamp[1])}'
    
    def exists(self) -> bool:
         return os.path.exists(self.file_path)

    def length(self) -> float:
        return self.absolute_timestamp[1] - self.absolute_timestamp[0]
    


