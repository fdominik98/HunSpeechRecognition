import os
from typing import Optional
from enum import Enum, unique
from utils.general_utils import timestamp_str

@unique
class AudioSource(Enum):
    ORIGINAL = 'Eredeti hangfájl'
    PREVIEWTEXT = 'Előnézet szöveg'
    SPLITLIST = 'Vágatlan szegmensek'
    TRIMLIST = 'Vágott szegmensek'

class AudioFile():
    def __init__(self, segment_number : int, file_path : str, absolute_timestamp : tuple[float, float],                
                 is_place_holder : bool = False) -> None:
        self.chunk_id = segment_number
        self.file_path = file_path
        self.absolute_timestamp = absolute_timestamp
        self.is_place_holder = is_place_holder
        self.length = self.absolute_timestamp[1] - self.absolute_timestamp[0]

    def __str__(self) -> str:
        if self.is_place_holder:
            return f'Üres {timestamp_str(self.absolute_timestamp)}'
        return f'{os.path.basename(self.file_path)} {timestamp_str(self.absolute_timestamp)}'
    
    def exists(self) -> bool:
         return os.path.exists(self.file_path)

