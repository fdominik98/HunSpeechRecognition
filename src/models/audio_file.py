import os
from utils.general_utils import to_timestamp_sec
from models.result_row import ResultRow

class AudioFile():
    def __init__(self, segment_number : int, file_path : str, relative_timestamp : tuple[float, float], absolute_timestamp : tuple[float, float]) -> None:
        self.segment_number = segment_number
        self.file_path = file_path
        self.relative_timestamp = relative_timestamp
        self.absolute_timestamp = absolute_timestamp

    def __str__(self) -> str:
        return f'{os.path.basename(self.file_path)} {to_timestamp_sec(self.relative_timestamp[0])}-{to_timestamp_sec(self.relative_timestamp[1])}'
    


class TextAudioFile(AudioFile):
    def __init__(self, result : ResultRow) -> None:
        super().__init__(result.chunk_id, result.chunk_file, result.relative_timestamp, result.absolute_timestamp)