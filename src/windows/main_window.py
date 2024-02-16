from customtkinter import CTkToplevel, CTkFrame, CTkTabview, CTkEntry
from models.settings import Settings
from models.process_state import ProcessState
from threads.mp3_splitter_thread import Mp3SplitterThread
from threads.mp3_trimmer_thread import Mp3TrimmerThread
from threads.pipeline_manager_thread import PipelineManagerThread
from frames.audio_player_frame import AudioPlayerFrame
from frames.init_process_frame import InitProcessFrame
from frames.audio_preview_frame import AudioPreviewFrame
from frames.result_preview_frame import ResultPreviewFrame
from frames.process_control_frame import ProcessControlFrame
from utils.window_utils import center_window, open_message
from threads.init_manager_thread import InitManagerThread
from models.pipeline_process import PipelineProcess

class MainWindow(CTkToplevel):
    def __init__(self, settings : Settings, pipeline_prcess : PipelineProcess):
        super().__init__()
        # configure window
        self.title("Beszéd Felismerés Prototípus")
        self.geometry("1100x720")
        center_window(self)
        
        self.settings : Settings = settings 

        self.message_window : CTkToplevel = None

        self.init_manager_thread  = InitManagerThread(settings=settings, error_callback=self.error_callback)
        self.init_manager_thread.start()

        # self.tabview = CTkTabview(self)
        # self.tabview.grid(row=0, column=0, pady=5, padx=5, sticky="new")

        # self.tab1 = self.tabview.add("tab 1")  # add tab at the end
        # self.tab2 = self.tabview.add("tab 2")  # add tab at the end
        # self.tabview.set("tab 1")  # set currently visible tab
        
        self.right_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.right_sidebar_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")


        self.audio_player_frame = AudioPlayerFrame(self.right_sidebar_frame, 1, 0)   


        self.result_prev_frame = ResultPreviewFrame(self.right_sidebar_frame, 0, 0, 
                                                    result_manager=self.init_manager_thread.result_manager,
                                                    audio_load_callback=self.audio_player_frame.load,
                                                    audio_play_callback=self.audio_player_frame.play)
        
                    


        # create sidebar frame with widgets
        self.left_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.left_sidebar_frame.grid(row=0, column=0, rowspan=2, padx=(0,5), sticky="nsew")


        self.init_process_frame = InitProcessFrame(self.left_sidebar_frame, 0, 0)             
        
        self.audio_preview_frame = AudioPreviewFrame(self.left_sidebar_frame, row=1, column=0,
                                                     settings=self.settings,
                                                     split_audio_manager=self.init_manager_thread.split_audio_manager,
                                                     trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager,
                                                     original_audio_manager=self.init_manager_thread.original_audio_manager,
                                                     audio_load_callback=self.audio_player_frame.load,
                                                     audio_play_callback=self.audio_player_frame.play)   

                                                     
                                                                
        self.process_control_frame = ProcessControlFrame(self.right_sidebar_frame, 2, 0,
                                                         settings=self.settings,
                                                         result_manager=self.init_manager_thread.result_manager,
                                                         process_state_change_callbacks=[self.on_process_state_change, 
                                                                            self.audio_preview_frame.on_process_state_change],
                                                         split_audio_manager=self.init_manager_thread.split_audio_manager,
                                                         trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager)
        
        self.right_sidebar_frame.grid_columnconfigure(0, weight=1)

        self.left_sidebar_frame.grid_rowconfigure(0, weight=0)
        self.left_sidebar_frame.grid_rowconfigure(1, weight=1)
        self.left_sidebar_frame.grid_columnconfigure(0, weight=1)


        self.grid_columnconfigure(0, weight=0, minsize=340)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.pipeline_process : PipelineProcess = pipeline_prcess       
        self.start_splitter_thread()
        self.start_trimmer_thread()
        self.start_pipeline_manager_thread()


    def destroy_threads(self):
        self.init_manager_thread.stop()
        self.trimmer_thread.stop()
        self.pipeline_manager_thread.stop()
        self.splitter_thread.stop()

        self.init_manager_thread.join()
        self.trimmer_thread.join()
        self.pipeline_manager_thread.join()
        self.splitter_thread.join()

    def __cancel_processing(self):  
        while not self.splitter_thread.input_queue.empty():
            self.splitter_thread.input_queue.get_nowait()
        while not self.trimmer_thread.input_queue.empty():
            self.trimmer_thread.input_queue.get_nowait()
        while not self.pipeline_manager_thread.input_queue.empty():
            self.pipeline_manager_thread.input_queue.get_nowait()
        
        self.pipeline_manager_thread.reset()
                 
    def on_process_state_change(self, process_state : ProcessState, forced : bool):
        if process_state == ProcessState.STOPPED:
            if forced:
                self.__cancel_processing()
        else:
            for task in self.init_manager_thread.asset_tree_manager.get():
                self.splitter_thread.input_queue.put(task.set_process_state(process_state))
                    

    def error_callback(self, message, thread):
        self.__cancel_processing()
        self.process_control_frame.switch_to_stop_mode()
        open_message(self, "hiba", f'{message} - {thread}') 


    def start_splitter_thread(self):
        self.splitter_thread = Mp3SplitterThread(settings = self.settings,
                                error_callback=self.error_callback,
                                split_audio_manager=self.init_manager_thread.split_audio_manager,
                                trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager)
        self.splitter_thread.start()
        
    def start_trimmer_thread(self):
        self.trimmer_thread = Mp3TrimmerThread(settings = self.settings,
                                        error_callback=self.error_callback,
                                        input_queue=self.splitter_thread.output_queue,
                                        split_audio_manager=self.init_manager_thread.split_audio_manager,
                                        trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager)
        self.trimmer_thread.start()

    def start_pipeline_manager_thread(self):
        self.pipeline_manager_thread = PipelineManagerThread(settings=self.settings,
                                process=self.pipeline_process,
                                input_queue=self.trimmer_thread.output_queue,
                                result_manager=self.init_manager_thread.result_manager,
                                error_callback=self.error_callback,
                                init_start_callback=self.init_process_frame.pipeline_init_start_callback,
                                init_finish_callback=self.init_process_frame.init_finish_callback)
        self.pipeline_manager_thread.start()
