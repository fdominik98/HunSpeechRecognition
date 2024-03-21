from models.process_state import ProcessState


class Task():
    def __init__(self, process_state: ProcessState,
                 segment_number: int,
                 main_file_path: str,
                 split_timestamp: tuple[float, float],
                 split_file_path: str,
                 trim_file_path: str) -> None:
        self.process_state: ProcessState = process_state
        self.chunk_id: int = segment_number
        self.main_file_path: str = main_file_path
        self.split_timestamp: tuple[float, float] = split_timestamp
        self.split_file_path: str = split_file_path
        self.trim_file_path: str = trim_file_path
        self.result_file_path: str = ''
        self.result_timestamp: tuple[float, float] = (0, 0)
        self.is_place_holder = False

    def get_audio_length(self) -> float:
        return self.result_timestamp[1] - self.result_timestamp[0]

    def set_process_state(self, process_state: ProcessState):
        self.process_state = process_state
        return self

    def set_main_file_path(self, path: str):
        self.main_file_path = path
        return self

    def set_split_file_path(self, path: str):
        self.split_file_path = path
        return self

    def set_split_timestamp(self, timestamp: tuple[float, float]):
        self.split_timestamp = timestamp
        return self

    def set_result_file_path(self, path: str):
        self.result_file_path = path
        return self

    def set_place_holder(self, is_place_holder: bool):
        self.is_place_holder = is_place_holder
        return self

    def set_result_timestamp(self, timestamp: tuple[float, float]):
        self.result_timestamp = timestamp
        return self
