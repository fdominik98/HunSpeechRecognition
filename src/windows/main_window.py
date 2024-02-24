from customtkinter import CTkToplevel, CTkFrame
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
from models.environment import get_images_path

class MainWindow(CTkToplevel):
    def __init__(self, master, settings : Settings, pipeline_prcess : PipelineProcess):
        super().__init__(master=master)
        # configure window
        center_window(self, 1100, 720)
        self.title("Transzkriptor Prototípus")
        self.iconbitmap(f'{get_images_path()}/icon.ico')
        self.bind('<Button-1>', self.on_widget_click)
        
        self.settings : Settings = settings 

        self.message_window : CTkToplevel = None

        self.init_manager_thread  = InitManagerThread(settings=settings, error_callback=self.error_callback)
        self.init_manager_thread.start()

        self.right_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.right_sidebar_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")


        self.audio_player_frame = AudioPlayerFrame(self.right_sidebar_frame, 1, 0, self.settings)   


        self.result_prev_frame = ResultPreviewFrame(self.right_sidebar_frame, 0, 0, 
                                                    result_manager=self.init_manager_thread.result_manager,
                                                    trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager,
                                                    audio_load_callback=self.audio_player_frame.load,
                                                    audio_play_callback=self.audio_player_frame.play)
        self.audio_player_frame.refresh_cursor_position = self.result_prev_frame.textbox.refresh_cursor_position
        self.audio_player_frame.unselect_result_preview = self.result_prev_frame.textbox.unselect
        
                    


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
                                                     audio_play_callback=self.audio_player_frame.play,
                                                    audio_stop_callback=self.audio_player_frame.stop)  
        self.audio_player_frame.unselect_splitting_textbox = self.audio_preview_frame.split_textbox.unselect 
        self.audio_player_frame.unselect_trimming_textbox = self.audio_preview_frame.trim_textbox.unselect

                                                     
                                                                
        self.process_control_frame = ProcessControlFrame(self.right_sidebar_frame, 2, 0,
                                                         settings=self.settings,
                                                         result_manager=self.init_manager_thread.result_manager,
                                                         process_state_change_callbacks=[self.on_process_state_change, 
                                                                            self.audio_preview_frame.on_process_state_change,
                                                                            self.result_prev_frame.on_process_state_change],
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
        self.splitter_thread = None
        self.trimmer_thread = None
        self.start_pipeline_manager_thread()

    def on_widget_click(self, event):
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)


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

    def __cancel_processing(self):  
        if self.splitter_thread is not None:
            self.splitter_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.join()
        if self.splitter_thread is not None:
            self.splitter_thread.join()
        self.pipeline_manager_thread.reset()
                 
    def on_process_state_change(self, process_state : ProcessState, forced : bool):
        if process_state is ProcessState.STOPPED:        
            self.__cancel_processing()
        else:
            self.start_splitter_thread()
            if process_state is ProcessState.TRIMMING or process_state is ProcessState.GENERATING:
                self.start_trimmer_thread()

            for task in self.init_manager_thread.asset_tree_manager.get():
                self.splitter_thread.input_queue.put(task.set_process_state(process_state))
                    

    def error_callback(self, message, thread):
        if self.splitter_thread is not None:
            self.splitter_thread.stop()
        if self.trimmer_thread is not None:
            self.trimmer_thread.stop()
        self.pipeline_manager_thread.stop()
        self.start_pipeline_manager_thread()
        
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
                                        output_queue=self.pipeline_manager_thread.input_queue,
                                        split_audio_manager=self.init_manager_thread.split_audio_manager,
                                        trimmed_audio_manager=self.init_manager_thread.trimmed_audio_manager,
                                        audio_stop_callback=self.audio_player_frame.stop_if_loaded)
        self.trimmer_thread.start()

    def start_pipeline_manager_thread(self):
        self.pipeline_manager_thread = PipelineManagerThread(settings=self.settings,
                                process=self.pipeline_process,
                                result_manager=self.init_manager_thread.result_manager,
                                error_callback=self.error_callback,
                                init_start_callback=self.init_process_frame.pipeline_init_start_callback,
                                init_finish_callback=self.init_process_frame.init_finish_callback)
        self.pipeline_manager_thread.start()
