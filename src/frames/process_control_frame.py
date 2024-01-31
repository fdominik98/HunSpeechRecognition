from customtkinter import CTkFrame, CTkProgressBar, CTkButton, CTkLabel
from utils.fonts import button_font, label_font
from models.settings import Settings
from managers.result_manager import ResultManager
from models.process_state import ProcessState
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager

class ProcessControlFrame(CTkFrame):
    def __init__(self, parent, row, column, settings: Settings, result_manager : ResultManager,
                 process_state_change_callbacks : list, split_audio_manager: SplitAudioFileManager, trimmed_audio_manager: TrimmedAudioFileManager):
        super().__init__(parent, height=70)
        self.process_state_change_callbacks : list = process_state_change_callbacks
        self.settings : Settings = settings
        self.result_manager : ResultManager = result_manager
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

        self.process_state : ProcessState = ProcessState.STOPPED

        self.grid(row=row, column=column, sticky="ewsn", pady=20)

        self.small_progressbar = CTkProgressBar(self, orientation="horizontal", width=350, height=5, corner_radius=0, determinate_speed=2.5)
        self.small_progressbar.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="wse")        
        self.small_progressbar.grid_remove()

        self.progressbar = CTkProgressBar(self, orientation="horizontal", width=350, height=20, corner_radius=0)
        self.progressbar.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="wne")        
        self.progressbar.grid_remove()

        self.progress_label = CTkLabel(self, text=f'{self.progressbar.get()} %', height=10,
                                              font=label_font())
        self.progress_label.grid(row=1, column=1, padx=0, pady=(0,10), sticky='wn')
        self.progress_label.grid_remove()

        self.split_start_button = CTkButton(self, fg_color="transparent", border_width=2, width=100, height=40, text_color=("gray10", "#DCE4EE")
                                                     , command=self.__on_start_splitting_click, text="Szegmentálás", font=button_font())
        self.split_start_button.grid(row=0, rowspan=3, column=1, padx=5, pady=(10, 10), sticky="se")

        self.trim_start_button = CTkButton(self, fg_color="transparent", border_width=2, width=100, height=40, text_color=("gray10", "#DCE4EE")
                                                     , command=self.__on_start_trimming_click, text="Trimmelés", font=button_font())
        self.trim_start_button.grid(row=0, rowspan=3, column=2, padx=5, pady=(10, 10), sticky="se")

        self.generation_start_button = CTkButton(self, fg_color="transparent", border_width=2, width=100, height=40, text_color=("gray10", "#DCE4EE")
                                                     , command=self.__on_start_generating_click, text="Generálás", font=button_font())
        self.generation_start_button.grid(row=0, rowspan=3, column=3, padx=(5, 20), pady=(10, 10), sticky="se")

        self.stop_button = CTkButton(self, fg_color="transparent", border_width=2, width=100, height=40, text_color=("gray10", "#DCE4EE")
                                                     , command=self.__on_cancel_process_click, text="Megszakítás", font=button_font())
        self.stop_button.grid(row=0, rowspan=3, column=3, padx=20, pady=(10, 10), sticky="se")
        self.stop_button.grid_remove()


        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.update_progress()


    def switch_to_stop_mode(self):        
        self.small_progressbar.grid_remove()
        self.small_progressbar.stop()
        self.progressbar.grid_remove()  
        self.progress_label.grid_remove()   

        self.stop_button.grid_remove()
        self.split_start_button.grid()
        self.trim_start_button.grid()
        self.generation_start_button.grid()  
    

    def __on_cancel_process_click(self):
        self.process_state = ProcessState.STOPPED
        self.__call_process_state_change_callbacks(True)       
        self.switch_to_stop_mode()

    def __on_start_splitting_click(self):
        self.process_state = ProcessState.SPLITTING
        self.__call_process_state_change_callbacks(True)       
        self.switch_to_process_mode()

    def __on_start_trimming_click(self):
        self.process_state = ProcessState.TRIMMING
        self.__call_process_state_change_callbacks(True)        
        self.switch_to_process_mode()

    def __on_start_generating_click(self):
        self.process_state = ProcessState.GENERATING
        self.__call_process_state_change_callbacks(True)       
        self.switch_to_process_mode()

    def __call_process_state_change_callbacks(self, forced : bool):
        for process_state_change_callback in self.process_state_change_callbacks:
            process_state_change_callback(self.process_state, forced) 

    def update_progress(self):
        if not self.winfo_exists():
            return
        if self.process_state == ProcessState.SPLITTING:
            new_value = (self.split_audio_manager.size() + self.trimmed_audio_manager.size()) / self.settings.chunk_count()
        elif self.process_state == ProcessState.TRIMMING:
            new_value = self.trimmed_audio_manager.size() / self.settings.chunk_count()
        elif self.process_state == ProcessState.GENERATING:
            new_value = self.result_manager.next_segment_num() / self.settings.chunk_count()
        else:
            new_value = 0
        self.progressbar.set(new_value)
        self.progress_label.configure(text=f'{self.process_state.value} {round(new_value * 100)} %') 
        if new_value >= 1.0:
            self.process_state = ProcessState.STOPPED
            self.__call_process_state_change_callbacks(False)
            self.switch_to_stop_mode()
        self.after(1000, self.update_progress)

    def switch_to_process_mode(self):        
        self.small_progressbar.grid()
        self.small_progressbar.start()
        self.progressbar.grid()  
        self.progress_label.grid()

        self.split_start_button.grid_remove()
        self.trim_start_button.grid_remove()
        self.generation_start_button.grid_remove()
        self.stop_button.grid()

        