from abc import ABC
from queue import Queue
from threading import Lock
from models.audio_file import AudioSource

class LoadableManager(ABC):
    def __init__(self, audio_source : AudioSource) -> None:
        super().__init__()
        self._lock = Lock()
        self.insert_widget_queue : Queue = Queue()
        self.delete_widget_queue : Queue = Queue()
        self.audio_source : AudioSource = audio_source