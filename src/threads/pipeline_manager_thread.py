from time import sleep
from threading import Event
from queue import Queue as ThreadQueue
from models.task import Task
from models.segment import Segment
from models.settings import Settings
from threads.speech_base_thread import SpeechBaseThread
from managers.result_manager import ResultManager
from models.pipeline_process import PipelineProcess, ModelInitState
from managers.audio_file_manager import AudioFileManager
from models.progress_data import ProgressData


class PipelineManagerThread(SpeechBaseThread):

    def __init__(self, settings: Settings, process: PipelineProcess,
                 result_manager: ResultManager, error_callback,
                 init_pipeline_queue: ThreadQueue, progress_data: ProgressData):
        super().__init__('PipelineManagerThread', settings, error_callback)
        self.process = process
        self.result_manager: ResultManager = result_manager
        self.input_queue: ThreadQueue = ThreadQueue()
        self.init_pipeline_queue: ThreadQueue = init_pipeline_queue
        self.progress_data: ProgressData = progress_data
        self.__reset_event = Event()

    def do_run(self):
        while not self.stopped():
            self.init_process()

            self.__reset_event.clear()

            while not self.stopped() and not self.reseted():
                if not self.input_queue.empty():
                    self.process_task(self.input_queue.get())

                if not self.process.output_queue.empty():
                    self.save_results(self.process.output_queue.get())
                    self.progress_data.step_trans_progress()
                sleep(1)

            self.process.terminate()
            self.process.join()

    def init_process(self):
        self.init_pipeline_queue.put(ModelInitState.INIT_STARTED)

        if not self.process.is_alive():
            self.process = PipelineProcess()
            self.process.start()

        while not self.stopped():
            if self.process.init_parent_conn.poll() and self.process.init_parent_conn.recv() is ModelInitState.INIT_FINISHED:
                self.init_pipeline_queue.put(ModelInitState.INIT_FINISHED)
                break
            sleep(0.5)

    def reset(self):
        self.__reset_event.set()

    def reseted(self):
        return self.__reset_event.is_set()

    def save_results(self, ready_task: tuple[list[Segment], Task]):
        result_list = self.result_manager.save_results(
            ready_task[0], ready_task[1])
        for result in result_list:
            self.result_manager.insert_widget_queue.put(result)
        print(f'saved new results')

    def process_task(self, task: Task):
        if not AudioFileManager.exists(task.result_file_path):
            self.progress_data.step_trans_progress()
            return

        if any(r.chunk_id == task.chunk_id for r in self.result_manager.get_all()):
            print(f'{task.result_file_path} already processed, skipping..')
            self.progress_data.step_trans_progress()
            return

        if task.is_place_holder:
            self.process.output_queue.put(([Segment('', 0, 0)], task))
            self.progress_data.step_trans_progress()
            return

        self.process.input_queue.put(task)
        return
