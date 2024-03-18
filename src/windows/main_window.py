from customtkinter import CTkToplevel, CTkFrame
from models.settings import Settings
from models.process_state import ProcessState
from frames.audio_player_frame import AudioPlayerFrame
from frames.init_pipeline_frame import InitPipelineFrame
from frames.audio_preview.audio_preview_frame import AudioPreviewFrame
from frames.result_preview_frame import ResultPreviewFrame
from frames.process_control_frame import ProcessControlFrame
from utils.window_utils import open_message
from models.pipeline_process import PipelineProcess
from managers.thread_manager import ThreadManager


class MainWindow(CTkToplevel):
    def __init__(self, master, settings: Settings, pipeline_prcess: PipelineProcess):
        super().__init__(master=master)
        self.withdraw()
        self.bind('<Button-1>', self.on_widget_click)
        self.message_window: CTkToplevel = None

        self.thread_manager: ThreadManager = ThreadManager(settings=settings,
                                                           pipeline_process=pipeline_prcess,
                                                           error_callback=self.error_callback)
        result_manager = self.thread_manager.init_manager_thread.result_manager
        split_audio_manager = self.thread_manager.init_manager_thread.split_audio_manager
        trimmed_audio_manager = self.thread_manager.init_manager_thread.trimmed_audio_manager
        original_audio_manager = self.thread_manager.init_manager_thread.original_audio_manager

        self.right_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.right_sidebar_frame.grid(
            row=0, column=1, padx=(5, 0), sticky="nsew")

        self.audio_player_frame = AudioPlayerFrame(
            self.right_sidebar_frame, 1, 0, settings)

        self.result_prev_frame = ResultPreviewFrame(self.right_sidebar_frame, 0, 0,
                                                    settings=settings,
                                                    result_manager=result_manager,
                                                    split_audio_file_manager=split_audio_manager,
                                                    trimmed_audio_file_manager=trimmed_audio_manager,
                                                    audio_load_callback=self.audio_player_frame.load,
                                                    audio_play_callback=self.audio_player_frame.on_play)
        self.audio_player_frame.refresh_cursor_position_callbacks.append(
            self.result_prev_frame.textbox.refresh_cursor_position)
        self.audio_player_frame.stop_playing_callbacks.append(
            self.result_prev_frame.textbox.unselect_all)

        # create sidebar frame with widgets
        self.left_sidebar_frame = CTkFrame(self, corner_radius=0)
        self.left_sidebar_frame.grid(
            row=0, column=0, rowspan=2, padx=(0, 5), sticky="nsew")

        self.init_pipeline_frame = InitPipelineFrame(
            self.left_sidebar_frame, 0, 0, self.thread_manager.init_pipeline_queue)

        self.audio_preview_frame = AudioPreviewFrame(self.left_sidebar_frame, row=1, column=0,
                                                     settings=settings,
                                                     split_audio_manager=split_audio_manager,
                                                     trimmed_audio_manager=trimmed_audio_manager,
                                                     original_audio_manager=original_audio_manager,
                                                     audio_load_callback=self.audio_player_frame.load,
                                                     audio_play_callback=self.audio_player_frame.on_play,
                                                     audio_stop_callback=self.audio_player_frame.on_stop)
        self.audio_player_frame.stop_playing_callbacks.append(
            self.audio_preview_frame.split_textbox.unselect_all)
        self.audio_player_frame.stop_playing_callbacks.append(
            self.audio_preview_frame.trim_textbox.unselect_all)

        self.process_control_frame = ProcessControlFrame(self.right_sidebar_frame, 2, 0,
                                                         settings=settings,
                                                         result_manager=result_manager,
                                                         process_state_change_callbacks=[self.on_process_state_change,
                                                                                         self.audio_preview_frame.on_process_state_change,
                                                                                         self.result_prev_frame.on_process_state_change],
                                                         split_audio_manager=split_audio_manager,
                                                         trimmed_audio_manager=trimmed_audio_manager,
                                                         progress_data=self.thread_manager.progress_data)
        self.audio_preview_frame.trim_switch_flip_callbacks.append(
            self.process_control_frame.on_trim_switch_flipped)

        self.right_sidebar_frame.grid_columnconfigure(0, weight=1)

        self.left_sidebar_frame.grid_rowconfigure(0, weight=0)
        self.left_sidebar_frame.grid_rowconfigure(1, weight=1)
        self.left_sidebar_frame.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=0, minsize=340)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def on_widget_click(self, event):
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)

    def destroy_threads(self):
        self.thread_manager.destroy_threads()

    def on_process_state_change(self, old_process_state: ProcessState, process_state: ProcessState, trim_enabled: bool, forced: bool):
        self.thread_manager.on_process_state_change(
            old_process_state, process_state,  trim_enabled, forced)

    def error_callback(self, message, thread):
        self.process_control_frame.switch_to_stop_mode()
        open_message(self, "hiba", f'{message} - {thread}')
