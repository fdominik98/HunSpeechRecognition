from datetime import datetime
from customtkinter import CTkFrame, CTkProgressBar, CTkButton, CTkLabel, CTkOptionMenu, NORMAL, DISABLED, StringVar
from utils.fonts import button_font, small_button_font, label_font
from models.settings import Settings
from managers.result_manager import ResultManager
from models.process_state import ProcessState, non_trimming_options
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager
from utils.general_utils import to_timestamp_sec
from models.progress_data import ProgressData


class ProcessControlFrame(CTkFrame):
    def __init__(self, parent, row, column, settings: Settings, result_manager: ResultManager,
                 process_state_change_callbacks: list, split_audio_manager: SplitAudioFileManager,
                 trimmed_audio_manager: TrimmedAudioFileManager, progress_data: ProgressData):
        super().__init__(parent, height=70)
        self.process_state_change_callbacks: list = process_state_change_callbacks
        self.settings: Settings = settings
        self.result_manager: ResultManager = result_manager
        self.split_audio_manager: SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager: TrimmedAudioFileManager = trimmed_audio_manager
        self.start_time: datetime = datetime.now()
        self.progress_data = progress_data

        self.process_state: ProcessState = ProcessState.STOPPED
        self.trim_enabled = settings.trim_switch_var

        self.grid(row=row, column=column, sticky="ews", pady=20)

        self.progressbar = CTkProgressBar(
            self, orientation="horizontal", width=250, height=20, corner_radius=0)
        self.progressbar.grid(row=0, column=0, padx=10,
                              pady=(20, 20), sticky="wns")
        self.progressbar.grid_remove()

        self.progress_label = CTkLabel(self, text=f'{self.progressbar.get()} %', height=10,
                                       font=label_font())
        self.progress_label.grid(row=0, column=0, padx=(
            15, 60), pady=(10, 10), sticky='ens')
        self.progress_label.grid_remove()

        self.progress_time_label = CTkLabel(
            self, text='', height=10, font=label_font())
        self.progress_time_label.grid(
            row=0, column=0, padx=(0, 0), pady=(10, 10), sticky='ens')
        self.progress_time_label.grid_remove()

        self.option_values = [
            str(choice) for choice in ProcessState if choice is not ProcessState.STOPPED]
        self.option_menu = CTkOptionMenu(self, variable=StringVar(value=str(ProcessState.SPLITTING)), values=self.option_values,
                                         font=small_button_font(), dropdown_font=small_button_font(), width=200)
        self.option_menu.grid(row=0, column=2, padx=(
            15, 15), pady=(10, 10), sticky="sne")

        self.transcription_start_button = CTkButton(self, fg_color="transparent", border_width=2, width=100, height=40, text_color=(
            "gray10", "#DCE4EE"), command=self.__on_start_generating_click, text="Indítás", font=button_font())
        self.transcription_start_button.grid(
            row=0, column=3, padx=(5, 20), pady=(10, 10), sticky="sne")

        self.stop_button = CTkButton(self, fg_color="transparent", border_width=2, width=100, height=40, text_color=(
            "gray10", "#DCE4EE"), command=self.__on_cancel_process_click, text="Megszakítás", font=button_font())
        self.stop_button.grid(row=0, column=3, padx=(
            5, 20), pady=(10, 10), sticky="sne")
        self.stop_button.grid_remove()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.on_trim_switch_flipped(self.settings.trim_switch_var)
        self.update_progress()

    def switch_to_stop_mode(self):
        self.process_state = ProcessState.STOPPED
        self.progressbar.grid_remove()
        self.progress_label.grid_remove()
        self.progress_time_label.grid_remove()
        self.option_menu.configure(state=NORMAL)
        self.stop_button.grid_remove()
        self.transcription_start_button.grid()

    def on_trim_switch_flipped(self, value: bool):
        self.trim_enabled = value
        if value:
            self.option_menu.configure(values=self.option_values)
        else:
            self.option_menu.configure(values=non_trimming_options)
        self.option_menu.configure(variable=StringVar(
            value=str(ProcessState.SPLITTING)))

    def __on_cancel_process_click(self):
        old_process_state = self.process_state
        self.switch_to_stop_mode()
        self.__call_process_state_change_callbacks(old_process_state, True)

    def __on_start_generating_click(self):
        old_process_state = self.process_state
        self.process_state = ProcessState.from_label(self.option_menu.get())
        self.switch_to_process_mode()
        self.__call_process_state_change_callbacks(old_process_state, True)

    def __call_process_state_change_callbacks(self, old_process_state: ProcessState, forced: bool):
        for process_state_change_callback in self.process_state_change_callbacks:
            process_state_change_callback(
                old_process_state, self.process_state, self.trim_enabled, forced)

    def update_progress(self):
        if not self.winfo_exists():
            return
        elapsed_time = (datetime.now() - self.start_time).seconds
        elapsed_time_ms = int(round((elapsed_time) * 1000))
        self.progress_time_label.configure(text=to_timestamp_sec(elapsed_time_ms))

        if self.process_state is ProcessState.SPLITTING:
            new_value = self.progress_data.get_split_progress()
        elif self.process_state is ProcessState.TRIMMING or self.process_state is ProcessState.SPLITTING_TRIMMING:
            new_value = self.progress_data.get_trim_progress()
        elif (self.process_state is ProcessState.TRANSCRIPTING or
                self.process_state is ProcessState.SPLITTING_TRANSCRIPTING or
                self.process_state is ProcessState.TRIMMING_TRANSCRIPTING or
                self.process_state is ProcessState.SPLITTING_TRIMMING_TRANSCRIPTING):
            new_value = self.progress_data.get_trans_progress()
        else:
            new_value = 0

        new_value = float(new_value) / self.settings.chunk_count
        self.progressbar.set(new_value)
        self.progress_label.configure(text=f'{round(new_value * 100)} %')
        if new_value >= 1.0:
            old_process_state = self.process_state
            self.switch_to_stop_mode()
            self.__call_process_state_change_callbacks(
                old_process_state, False)
        self.after(1000, self.update_progress)

    def switch_to_process_mode(self):
        self.start_time = datetime.now()
        self.progressbar.grid()
        self.progress_label.grid()
        self.progress_time_label.configure(text=to_timestamp_sec(0))
        self.progress_time_label.grid()
        self.option_menu.configure(state=DISABLED)
        self.transcription_start_button.grid_remove()
        self.stop_button.grid()
