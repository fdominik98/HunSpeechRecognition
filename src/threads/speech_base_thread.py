import traceback
import logging
from threading import Thread, Event
from abc import ABC, abstractmethod
from models.settings import Settings

class SpeechBaseThread(Thread, ABC):    
    daemon = True

    def __init__(self, thread_name : str, settings : Settings, error_callback):
        Thread.__init__(self)
        self.name : str = thread_name
        self.settings : Settings = settings
        self.error_callback = error_callback
        self.__stop_event = Event()
        self.__reset_event = Event()

    def run(self):  
        try:
           self.do_run()
           print(f"{self.name} terminated gracefully.")           
        except Exception as e:
           logging.getLogger().error(e)
           traceback.print_exc()
           self.error_callback(e, self.name)

    @abstractmethod
    def do_run(self):
        pass

    def stop(self):
        self.__stop_event.set()

    def stopped(self):
        return self.__stop_event.is_set()
    
    def reset(self):
        self.__reset_event.set()

    def paused(self):
        return self.__reset_event.is_set()
    
    def resume(self):
        self.__reset_event.clear()