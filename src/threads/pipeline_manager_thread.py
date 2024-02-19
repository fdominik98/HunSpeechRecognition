import os
from time import sleep
from multiprocessing import Queue as ProcessQueue
from queue import Queue as ThreadQueue
from models.task import Task
from models.segment import Segment
from models.settings import Settings
from threads.speech_base_thread import SpeechBaseThread
from managers.result_manager import ResultManager
from models.pipeline_process import PipelineProcess

class PipelineManagerThread(SpeechBaseThread): 

    def __init__(self, settings : Settings, process: PipelineProcess, input_queue : ThreadQueue, result_manager, error_callback, init_start_callback,
                  init_finish_callback):
        super().__init__('PipelineManagerThread', settings, error_callback)
        self.process = process
        self.result_manager : ResultManager = result_manager
        self.input_queue : ThreadQueue = input_queue
        self.init_finish_callback = init_finish_callback    
        self.init_start_callback = init_start_callback
        self.ready_tasks : list[tuple[list[Segment], Task]] = []

    def do_run(self):
        while not self.stopped():
            if not self.process.is_alive():
                self.process = PipelineProcess()
                self.process.start()
            
            self.init_start_callback()
            while not self.stopped():
                if self.process.parent_conn.poll() and self.process.parent_conn.recv() == 'init_finished':                
                    self.init_finish_callback()
                    break
                sleep(0.5)        

            while not self.stopped() and not self.paused(): 
                if not self.input_queue.empty():                  
                        self.process_task(self.process.input_queue, self.input_queue.get())

                if not self.process.output_queue.empty():
                    self.save_results(self.process.output_queue.get())

                sleep(0.5)

            self.resume()
            self.process.terminate()
            self.process.join()


    def save_results(self, ready_task : tuple[list[Segment], Task]):
        self.ready_tasks.append(ready_task)
        saved_tasks : list[tuple[list[Segment], Task]] = []
        while True:
            for segments, task in self.ready_tasks:
                if task.segment_number == self.result_manager.next_segment_num():
                    result_list = self.result_manager.save_results(segments, task)
                    for result in result_list:
                        self.result_manager.insert_widget_queue.put(result)
                    saved_tasks.append((segments, task))
            if len(saved_tasks) == 0:
                break
            filtered_tasks : list[tuple[list[Segment], Task]] = []
            for segments1, task1 in self.ready_tasks:
                if not any(task1.segment_number == task2.segment_number for _, task2 in saved_tasks):
                    filtered_tasks.append((segments1, task1))
            self.ready_tasks = filtered_tasks
            saved_tasks = []
            print(f'saved new results')


    def process_task(self, input_queue : ProcessQueue, task : Task):    
        if not os.path.exists(task.trim_file_path):
            return

        if any(r.chunk_file == task.trim_file_path for r in self.result_manager.get_all()):
            print(f'{task.trim_file_path} already processed, skipping..')
            return
        
        input_queue.put(task)
        
