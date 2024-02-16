from customtkinter import CTkTextbox, END, CURRENT, NONE
from utils.fonts import textbox_font
from managers.result_manager import ResultManager
from managers.audio_file_manager import AudioFileManager
from models.audio_file import TextAudioFile, AudioSource
from abc import ABC, abstractmethod

class InteractiveTextbox(CTkTextbox, ABC):
    def __init__(self, master, audio_load_callback, audio_play_callback, width=200, height=200):
        super().__init__(master, width=width, height=height, font=textbox_font(), text_color='black', fg_color='#D3D3D3', wrap=NONE)
        self.audio_load_callback = audio_load_callback
        self.audio_play_callback = audio_play_callback

        self.selected_tag = 'selected_tag'
        self.tag_config(self.selected_tag, background="#999999")
        self.bind("<Button-1>", command=self.on_text_click)
        self.bind("<Double-1>", command=self.on_text_double_click)

        self.configure(state="disabled")

    def on_text_click(self, event):
        self.tag_remove(self.selected_tag, '1.0', END)
        current_index = self.get_current_index()
        self.tag_add(self.selected_tag, f'{current_index + 1}.0', f'{current_index + 1}.end')
        self.load_file(current_index)

    @abstractmethod
    def load_file(self, index):
        pass

    def get_current_index(self) -> int:
        return int(self.index(CURRENT).split('.')[0]) - 1

    def on_text_double_click(self, event):
        self.on_text_click(event)
        self.audio_play_callback()

    def insert_row(self, row_id : int, text : str):
        if row_id == -1:
            row_id = self.row_count() + 1
        if row_id < 1 or row_id > self.row_count() + 1:
            print(f'Cannot insert row: invalid row_id ({row_id}) while size is {self.row_count()}')
            return
        self.configure(state='normal')
        self.insert(f'{row_id}.0', text + '\n')
        self.configure(state='disabled')

    def delete_row(self, row_id : int):
        if row_id < 1 or row_id > self.row_count():
            print(f'Cannot delete row: invalid row_id ({row_id}) while size is {self.row_count()}')
            return
        self.configure(state='normal')
        start_index = f'{row_id}.0'
        end_index = f'{row_id+1}.0'
        self.delete(start_index, end_index)
        self.configure(state='disabled')

    def row_count(self):
        last_char_index = self.index('end-1c')
        return int(last_char_index.split('.')[0])


class AudioInteractiveTextbox(InteractiveTextbox):
    def __init__(self, audio_file_manager : AudioFileManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_file_manager : AudioFileManager = audio_file_manager

    def load_file(self, index):
        if index > self.audio_file_manager.size() - 1:
            return
        audio_file = self.audio_file_manager.get(index)
        self.audio_load_callback(self.audio_file_manager.audio_source, audio_file)


class ResultInteractiveTextbox(InteractiveTextbox):
    def __init__(self, result_manager : ResultManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result_manager : ResultManager = result_manager

    def load_file(self, index):
        if index > self.result_manager.size() - 1:
            return
        result = self.result_manager.get(index)
        self.audio_load_callback(AudioSource.PREVIEWTEXT, TextAudioFile(result))