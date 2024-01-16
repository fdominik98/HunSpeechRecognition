import threading
from abc import ABC, abstractmethod
from models.settings import Settings
from models.process_state import ProcessState 

class SpeechBaseThread(threading.Thread, ABC):    
    daemon = True

    def __init__(self, thread_name : str, settings : Settings, process_state : ProcessState, error_callback):
        threading.Thread.__init__(self)
        self.name : str = thread_name
        self.settings : Settings = settings
        self.process_state : ProcessState = process_state
        self.error_callback = error_callback
        self._stop_event = threading.Event()

    def run(self):  
        try:
           self.do_run()
           print(f"{self.name} terminated gracefully.")           
        except Exception as e:
           self.error_callback(e)

    @abstractmethod
    def do_run(self):
        pass

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()