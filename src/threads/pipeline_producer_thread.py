from datetime import datetime
from multiprocessing import Queue as ProcessQueue
from threading import Thread, Event
from queue import Queue as ThreadQueue
from models.task import Task
from models.segment import Segment


class PipelineProducerThread(Thread):
    daemon = True

    def __init__(self, id: int, model, output_queue: ProcessQueue):
        Thread.__init__(self)
        self.name = f"Producer-{id}"
        self.__model = model
        self.input_queue: ThreadQueue = ThreadQueue()
        self.__output_queue = output_queue
        self.__busy_event = Event()

    def run(self):
        while (True):
            task: Task = self.input_queue.get()
            self.__busy_event.set()
            print(f'{self.name} received task {datetime.now()}')
            segments = self.__model.transcribe(audio=task.result_file_path,
                                              condition_on_previous_text=True, **{"language": "hu", "fp16" : False})
            result = ([Segment(s['text'], int(round(s['start'] * 1000)), int(round(s['end'] * 1000)))
                      for s in segments['segments']], task, segments['text'])  
            self.__output_queue.put(result)
            self.__busy_event.clear()
            print(f'{self.name} finished task {datetime.now()}')

    def is_free(self):
        return not self.__busy_event.is_set()
