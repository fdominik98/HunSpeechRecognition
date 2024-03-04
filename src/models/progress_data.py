from threading import Lock

class ProgressData():
    def __init__(self) -> None:
        self.__lock = Lock()
        self.__split_progress = 0
        self.__trim_progress = 0
        self.__trans_progress = 0

    def step_split_progress(self):
        with self.__lock:
            self.__split_progress += 1

    def step_trim_progress(self):
        with self.__lock:
            self.__trim_progress += 1

    def step_trans_progress(self):
        with self.__lock:
            self.__trans_progress += 1

    def reset(self):
        with self.__lock:
            self.__split_progress = 0
            self.__trim_progress = 0
            self.__trans_progress = 0

    def get_split_progress(self) -> int:
        with self.__lock:
            return self.__split_progress
        
    def get_trim_progress(self) -> int:
        with self.__lock:
            return self.__trim_progress
        
    def get_trans_progress(self) -> int:
        with self.__lock:
            return self.__trans_progress
    
        
