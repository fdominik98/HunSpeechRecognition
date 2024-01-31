from customtkinter import CTkTextbox, END, CURRENT
from managers.result_manager import ResultManager
from utils.general_utils import generate_hash, to_timestamp_1dec
from models.audio_source import AudioSource
from models.audio_file import TextAudioFile
from models.result_row import ResultRow

class InteractiveTextManager():
    def __init__(self, result_manager, textbox : CTkTextbox, audio_load_callback, audio_play_callback) -> None:
        self.textbox = textbox
        self.audio_load_callback = audio_load_callback
        self.audio_play_callback = audio_play_callback
        self.result_manager : ResultManager = result_manager

        self.selected_tag = 'selected_tag'
        self.textbox.tag_config(self.selected_tag, background="#999999")
        self.textbox.bind("<Button-1>", command=self.on_text_click)
        self.textbox.bind("<Double-1>", command=self.on_text_double_click)

    def on_text_click(self, event):
        result = self.result_manager.find_by_text_pos(index=self.textbox.index(CURRENT))
        self.textbox.tag_remove(self.selected_tag, '1.0', END)
        if result is None:
            return
        self.textbox.tag_add(self.selected_tag, f'{result.id + 1}.0', f'{result.id + 1}.end')
        self.audio_load_callback(AudioSource.PREVIEWTEXT, TextAudioFile(result))

    def on_text_double_click(self, event):
        self.on_text_click(event)
        self.audio_play_callback()


    def refresh(self):
        self.textbox.configure(state='normal')
        self.textbox.delete("1.0", END)

        for result in self.result_manager.get_all():
            self.insert_text(result)

        self.textbox.configure(state='disabled')

    def insert_text(self, result : ResultRow):
        self.textbox.configure(state='normal')

        self.textbox.insert(f'{result.id + 1}.0', result.sentence + '\n')
        #self.textbox.insert(END, " ")

        self.textbox.configure(state='disabled')


