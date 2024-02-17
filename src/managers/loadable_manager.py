from abc import ABC, abstractmethod
from threading import Lock
from models.audio_file import AudioSource
from queue import Queue

class LoadableManager(ABC):
    def __init__(self, audio_source : AudioSource) -> None:
        super().__init__()
        self._lock = Lock()
        self.insert_widget_queue : Queue = Queue()
        self.delete_widget_queue : Queue = Queue()
        self.audio_source : AudioSource = audio_source


    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get(self, index : int):
        pass

    @abstractmethod    
    def size(self):
        pass
