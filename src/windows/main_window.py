from customtkinter import CTkToplevel, CTkFrame
from models.settings import Settings
from models.process_state import ProcessState
from threads.mp3_splitter_thread import Mp3SplitterThread
from threads.mp3_trimmer_thread import Mp3TrimmerThread
from threads.pipeline_manager_thread import PipelineManagerThread
from queue import Queue
from managers.interactive_text_manager import InteractiveTextManager
from frames.audio_player_frame import AudioPlayerFrame
from frames.init_process_frame import InitProcessFrame
from frames.audio_preview_frame import AudioPreviewFrame
from frames.result_preview_frame import ResultPreviewFrame
from frames.process_control_frame import ProcessControlFrame
from utils.window_utils import center_window, open_message
from threads.init_manager_thread import InitManagerThread

class MainWindow(CTkToplevel):
    def __init__(self, settings : Settings):
        super().__init__()
        # configure window
        self.title("Beszéd Felismerés Prototípus")
        self.geometry("1100x720")
        center_window(self)
        
        self.settings : Settings = settings        

        self.trimming_queue : Queue = Queue()
        self.pipeline_queue : Queue = Queue()
        self.splitter_thread : Mp3SplitterThread = None
        self.trimmer_thread : Mp3TrimmerThread= None 
        self.pipeline_manager_thread : PipelineManagerThread = None

        self.message_window : CTkToplevel = None

        self.init_manager_thread  = InitManagerThread(settings=settings,
                                                    process_state=ProcessState.STOPPED,
                                                    error_callback=self.error_callback)
        self.init_manager_thread.start()

        
        self.right_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.right_sidebar_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")


        self.audio_player_frame = AudioPlayerFrame(self.right_sidebar_frame, 1, 0)   

        self.interactive_text_manager = InteractiveTextManager(result_manager=self.init_manager_thread.result_manager,
                                                               audio_load_callback=self.audio_player_frame.load)

        self.result_prev_frame = ResultPreviewFrame(self.right_sidebar_frame, 0, 0,
                                                    interactive_text_manager=self.interactive_text_manager)
        
        self.process_control_frame = ProcessControlFrame(self.right_sidebar_frame, 2, 0,
                                                         settings=self.settings,
                                                         result_manager=self.init_manager_thread.result_manager,
                                                         start_process_callback=self.on_start_process,
                                                         cancel_process_callback=self.on_cancel_processing,
                                                         split_audio_manager=self.init_manager_thread.split_audio_manager,
                                                         trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager)
        
        self.right_sidebar_frame.grid_columnconfigure(0, weight=1)
                    


        # create sidebar frame with widgets
        self.left_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.left_sidebar_frame.grid(row=0, column=0, rowspan=2, padx=(0,5), sticky="nsew")


        self.init_process_frame = InitProcessFrame(self.left_sidebar_frame, 0, 0)             
        
        self.audio_preview_frame = AudioPreviewFrame(self.left_sidebar_frame, row=1, column=0,
                                                     settings=self.settings,
                                                     split_audio_manager=self.init_manager_thread.split_audio_manager,
                                                     trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager,
                                                     original_audio_manager=self.init_manager_thread.original_audio_manager,
                                                     load_audio_callback=self.audio_player_frame.load)              

        self.left_sidebar_frame.grid_rowconfigure(0, weight=0)
        self.left_sidebar_frame.grid_rowconfigure(1, weight=1)
        self.left_sidebar_frame.grid_columnconfigure(0, weight=1)


        self.grid_columnconfigure(0, weight=0, minsize=340)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.start_pipeline_manager_thread(ProcessState.STOPPED)      


    def destroy_threads(self):
        if self.init_manager_thread:
            self.init_manager_thread.stop()
        if self.trimmer_thread:
            self.trimmer_thread.stop()
        if self.pipeline_manager_thread:
            self.pipeline_manager_thread.stop()
        if self.splitter_thread:
            self.splitter_thread.stop()

        if self.init_manager_thread:
            self.init_manager_thread.join()
        if self.trimmer_thread:
            self.trimmer_thread.join()
        if self.pipeline_manager_thread:
            self.pipeline_manager_thread.join()
        if self.splitter_thread:
            self.splitter_thread.join()

    def on_cancel_processing(self):  
        self.destroy_threads()
        self.trimming_queue.empty()
        self.pipeline_queue.empty()
        self.start_pipeline_manager_thread(ProcessState.STOPPED)
                 
    def on_start_process(self, process_state : ProcessState):
        self.start_splitter_thread(process_state)
        if process_state == ProcessState.TRIMMING or process_state == ProcessState.GENERATING:
            self.start_trimmer_thread(process_state)
                    
    def error_callback(self, message):
        self.on_cancel_processing()
        self.process_control_frame.switch_to_stop_mode()
        open_message(self, "hiba", message) 


    def pipeline_success_callback(self):
        self.process_control_frame.switch_to_stop_mode()
        print('pipeline finished successfuly.') 
                        


    def start_pipeline_manager_thread(self, process_state: ProcessState):
        self.pipeline_manager_thread = PipelineManagerThread(settings=self.settings,
                                process_state=process_state,
                                result_manager=self.init_manager_thread.result_manager,
                                error_callback=self.error_callback,
                                pipeline_queue=self.pipeline_queue,
                                init_start_callback=self.init_process_frame.pipeline_init_start_callback,
                                init_finish_callback=self.init_process_frame.init_finish_callback,
                                pipeline_success_callback=self.pipeline_success_callback)
        self.pipeline_manager_thread.start()
    
    def start_splitter_thread(self, process_state: ProcessState):
        self.splitter_thread = Mp3SplitterThread(settings = self.settings,
                                process_state=process_state,                                                 
                                error_callback=self.error_callback,
                                trimming_queue=self.trimming_queue,
                                split_audio_manager=self.init_manager_thread.split_audio_manager,
                                trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager)
        self.splitter_thread.start()
        
    def start_trimmer_thread(self, process_state: ProcessState):
        self.trimmer_thread = Mp3TrimmerThread(settings = self.settings,
                                        process_state=process_state,
                                        error_callback=self.error_callback,
                                        trimming_queue=self.trimming_queue,
                                        pipeline_queue=self.pipeline_queue,
                                        split_audio_manager=self.init_manager_thread.split_audio_manager,
                                        trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager)
        self.trimmer_thread.start()
