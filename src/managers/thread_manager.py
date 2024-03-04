from copy import deepcopy
from queue import Queue
from typing import Optional
from models.settings import Settings
from models.process_state import ProcessState
from threads.audio_splitter_thread import AudioSplitterThread
from threads.audio_trimmer_thread import AudioTrimmerThread
from threads.pipeline_manager_thread import PipelineManagerThread
from threads.init_manager_thread import InitManagerThread
from models.pipeline_process import PipelineProcess
from models.progress_data import ProgressData

class ThreadManager():
    def __init__(self, settings : Settings, pipeline_process : PipelineProcess, error_callback) -> None:
        self.settings = settings
        self.pipeline_process = pipeline_process
        self.main_window_error_callback = error_callback

        self.init_pipeline_queue : Queue = Queue()

        self.progress_data = ProgressData()

        self.init_manager_thread  = InitManagerThread(settings=settings, error_callback=self.error_callback)
        self.init_manager_thread.start()

        self.splitter_thread : Optional[AudioSplitterThread] = None
        self.trimmer_thread : Optional[AudioTrimmerThread] = None
        self.start_pipeline_manager_thread()

    def destroy_threads(self):
        if self.splitter_thread is not None:
            self.splitter_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.stop()
        self.pipeline_manager_thread.stop()
        self.init_manager_thread.stop()
        self.init_manager_thread.join()
        self.pipeline_manager_thread.join()
        if self.trimmer_thread is not None:
            self.trimmer_thread.join()
        if self.splitter_thread is not None:
            self.splitter_thread.join()

    def cancel_processing(self, old_process_state : ProcessState):  
        if self.splitter_thread is not None:
            self.splitter_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.join()
        if self.splitter_thread is not None:
            self.splitter_thread.join()
        if not (old_process_state is ProcessState.SPLITTING or
                 old_process_state is ProcessState.SPLITTING_TRIMMING or
                   old_process_state is ProcessState.TRIMMING):
            self.pipeline_manager_thread.reset()


    def error_callback(self, message, thread):
        if self.splitter_thread is not None:
            self.splitter_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.stop()
        self.pipeline_manager_thread.stop()
        self.start_pipeline_manager_thread()        
        self.main_window_error_callback( message, thread)


    def start_splitter_thread(self, output_queue : Queue):
        self.splitter_thread = AudioSplitterThread(settings = self.settings,
                                error_callback=self.error_callback,
                                output_queue=output_queue,
                                split_audio_manager=self.init_manager_thread.split_audio_manager,
                                trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager,
                                progress_data=self.progress_data)
        self.splitter_thread.start()
        
    def start_trimmer_thread(self, input_queue : Queue, output_queue : Queue):
        self.trimmer_thread = AudioTrimmerThread(settings = self.settings,
                                        error_callback=self.error_callback,
                                        input_queue=input_queue,
                                        output_queue=output_queue,
                                        split_audio_manager=self.init_manager_thread.split_audio_manager,
                                        trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager,
                                        progress_data=self.progress_data)
        self.trimmer_thread.start()

    def start_pipeline_manager_thread(self):
        self.pipeline_manager_thread = PipelineManagerThread(settings=self.settings,
                                process=self.pipeline_process,
                                result_manager=self.init_manager_thread.result_manager,
                                error_callback=self.error_callback,
                                init_pipeline_queue=self.init_pipeline_queue,
                                progress_data=self.progress_data)
        self.pipeline_manager_thread.start()


    def on_process_state_change(self, old_process_state : ProcessState, process_state : ProcessState, trim_enabled : bool, forced : bool):
        if process_state is ProcessState.STOPPED:        
           self.cancel_processing(old_process_state)
        else:
            self.init_processing()
            input_queue : Queue = Queue()
            if process_state is ProcessState.TRIMMING:
                self.start_trimmer_thread(input_queue=input_queue, output_queue=Queue())

            elif process_state is ProcessState.TRANSCRIPTING:
                input_queue = self.pipeline_manager_thread.input_queue

            elif process_state is ProcessState.TRIMMING_TRANSCRIPTING:
                self.start_trimmer_thread(input_queue=input_queue, output_queue=self.pipeline_manager_thread.input_queue)

            elif process_state is ProcessState.SPLITTING:
                self.start_splitter_thread(output_queue=Queue())
                input_queue = self.splitter_thread.input_queue

            elif process_state is ProcessState.SPLITTING_TRANSCRIPTING:
                self.start_splitter_thread(output_queue=self.pipeline_manager_thread.input_queue)
                input_queue = self.splitter_thread.input_queue

            elif process_state is ProcessState.SPLITTING_TRIMMING:
                trim_input_queue : Queue = Queue()
                self.start_splitter_thread(output_queue=trim_input_queue)
                self.start_trimmer_thread(input_queue=trim_input_queue, output_queue=Queue())
                input_queue = self.splitter_thread.input_queue

            elif process_state is ProcessState.SPLITTING_TRIMMING_TRANSCRIPTING:
                trim_input_queue : Queue = Queue()
                self.start_splitter_thread(output_queue=trim_input_queue)
                self.start_trimmer_thread(input_queue=trim_input_queue, output_queue=self.pipeline_manager_thread.input_queue)
                input_queue = self.splitter_thread.input_queue
            else:
                return    

            for task in self.init_manager_thread.asset_tree_manager.get():
                _task = deepcopy(task).set_process_state(process_state)
                if trim_enabled:
                    _task.set_result_file_path(task.trim_file_path)
                    audio_file = self.init_manager_thread.trimmed_audio_manager.get_by_path(task.trim_file_path)
                    if audio_file is not None:
                        _task.set_result_timestamp(audio_file.absolute_timestamp)
                else:
                    _task.set_result_file_path(task.split_file_path)
                    _task.set_result_timestamp(task.split_timestamp)
                input_queue.put(_task)

    def init_processing(self):
        while not self.pipeline_manager_thread.input_queue.empty():
            self.pipeline_manager_thread.input_queue.get()
        self.progress_data.reset()