import os
from enum import Enum, unique
from utils.general_utils import timestamp_str


@unique
class AudioSource(Enum):
    ORIGINAL = 'Eredeti hangfájl'
    PREVIEWTEXT = 'Előnézet szöveg'
    SPLITLIST = 'Vágatlan szegmensek'
    TRIMLIST = 'Vágott szegmensek'


class AudioFile():
    def __init__(self, segment_number: int, file_path: str, absolute_timestamp: tuple[int, int],
                 is_place_holder: bool = False) -> None:
        self.chunk_id : int= segment_number
        self.file_path : str = file_path
        self.absolute_timestamp : tuple[int, int] = absolute_timestamp
        self.is_place_holder : bool = is_place_holder
        self.length : int = self.absolute_timestamp[1] - self.absolute_timestamp[0]

    def __str__(self) -> str:
        if self.is_place_holder:
            return f'{self.chunk_id + 1}. ({timestamp_str(self.absolute_timestamp)}) Üres'
        return f'{self.chunk_id + 1}. ({timestamp_str(self.absolute_timestamp)}) {os.path.basename(self.file_path)}'

    def exists(self) -> bool:
        return os.path.exists(self.file_path)

    def __eq__(self, other):
        if isinstance(other, AudioFile):
            return self.chunk_id == other.chunk_id and self.file_path == other.file_path
        return False
