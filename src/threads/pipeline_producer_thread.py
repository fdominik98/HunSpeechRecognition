from datetime import datetime
from multiprocessing import Queue as ProcessQueue
from threading import Thread, Event
from queue import Queue as ThreadQueue
from faster_whisper import WhisperModel
from models.task import Task
from models.segment import Segment

class PipelineProducerThread(Thread): 
    daemon = True

    def __init__(self, id: int, model : WhisperModel, output_queue: ProcessQueue):
        Thread.__init__(self)
        self.name = f"Producer-{id}"
        self.__model = model
        self.input_queue : ThreadQueue = ThreadQueue()
        self.__output_queue = output_queue
        self.__busy_event = Event()

    def run(self):  
        while(True):
            task : Task = self.input_queue.get()
            self.__busy_event.set()
            print(f'{self.name} received task {datetime.now()}')
            segments, _ = self.__model.transcribe(audio=task.result_file_path, language='hu')
            self.__output_queue.put(([Segment(s.text, s.start, s.end) for s in segments], task))  
            self.__busy_event.clear()
            print(f'{self.name} finished task {datetime.now()}')

    def is_free(self):
        return not self.__busy_event.is_set() 