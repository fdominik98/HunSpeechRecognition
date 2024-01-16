from threads.speech_base_thread import SpeechBaseThread
from managers.result_manager import ResultManager
from multiprocessing import Queue as ProcessQueue
import os
from time import sleep
from queue import Queue as threadQueue
from models.task import Task
from models.settings import Settings
from models.process_state import ProcessState
from models.pipeline_process import PipelineProcess

class PipelineManagerThread(SpeechBaseThread): 

    def __init__(self, settings : Settings, process_state : ProcessState, result_manager, error_callback, pipeline_queue, init_start_callback,
                  init_finish_callback, pipeline_success_callback):
        super().__init__('PipelineManagerThread', settings, process_state, error_callback)
        self.result_manager : ResultManager = result_manager
        self.pipeline_queue : threadQueue = pipeline_queue
        self.init_finish_callback = init_finish_callback    
        self.pipeline_success_callback = pipeline_success_callback
        self.init_start_callback = init_start_callback

    def do_run(self):
        process = PipelineProcess()
        process.start()
        
        self.init_start_callback()
        while not self.stopped():
           if process.parent_conn.poll() and process.parent_conn.recv() == 'init_finished':                
                self.init_finish_callback()
                break
           sleep(0.5)
        

        while not self.stopped(): 
           if not self.pipeline_queue.empty():  
                if self.process_task(process.input_queue, self.pipeline_queue.get()):
                    self.pipeline_success_callback()                
                                    
           if not process.output_queue.empty():
               result_list = process.output_queue.get()
               self.result_manager.save_results(result_list)
               print(f'saved new results')
               for result in result_list:
                    self.result_manager.widget_queue.put(result)
           sleep(0.5)

        process.terminate()
        process.join()

    def process_task(self, input_queue : ProcessQueue, task : Task):
        if task == None:
            return True

        if not os.path.exists(task.trim_file_path):
            return False

        print('Data to process received')

        if any(r.chunk_file == task.trim_file_path for r in self.result_manager.get()):
            print(f'{task.trim_file_path} already processed, skipping..')
            return False
        
        input_queue.put(task)
        
