class Task():
    def __init__(self, segment_number : int, main_file_path : str, split_file_path : str, split_timestamp : tuple[float, float], 
                trim_file_path : str, trim_timestamp : tuple[float, float] = '') -> None:
        self.segment_number = segment_number
        self.main_file_path = main_file_path
        self.split_file_path = split_file_path
        self.split_timestamp = split_timestamp
        self.trim_file_path = trim_file_path
        self.trim_timestamp = trim_timestamp

    def set_main_file_path(self, path : str):
        self.main_file_path = path
        return self
    
    def set_split_file_path(self, path : str):
        self.split_file_path = path
        return self
    
    def set_split_timestamp(self, timestamp : str):
        self.split_timestamp = timestamp
        return self
    
    def set_trim_file_path(self, path : str):
        self.trim_file_path = path
        return self
    
    def set_trim_timestamp(self, timestamp : str):
        self.trim_timestamp = timestamp
        return self
    