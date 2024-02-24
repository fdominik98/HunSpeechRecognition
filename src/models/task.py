from models.process_state import ProcessState

class Task():
    def __init__(self, process_state : ProcessState,
                segment_number : int,
                main_file_path : str,
                split_timestamp : tuple[float, float],
                trim_file_path : str,
                split_file_path : str) -> None:
        self.process_state : ProcessState = process_state
        self.segment_number : int = segment_number
        self.main_file_path : str = main_file_path
        self.split_file_path : str = split_file_path
        self.split_timestamp : tuple[float, float] = split_timestamp
        self.trim_file_path : str = trim_file_path
        self.trim_timestamp : tuple[float, float] = (0,0)
        self.is_place_holder = False

    def set_process_state(self, process_state : ProcessState):
        self.process_state = process_state
        return self

    def set_main_file_path(self, path : str):
        self.main_file_path = path
        return self
    
    def set_split_file_path(self, path : str):
        self.split_file_path = path
        return self
    
    def set_split_timestamp(self, timestamp : tuple[float, float]):
        self.split_timestamp = timestamp
        return self
    
    def set_trim_file_path(self, path : str):
        self.trim_file_path = path
        return self
    
    def set_place_holder(self, is_place_holder : bool):
        self.is_place_holder = is_place_holder
        return self
    
    def set_trim_timestamp(self, timestamp : tuple[float, float]):
        self.trim_timestamp = timestamp
        return self
    