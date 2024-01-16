from customtkinter import CTkTextbox, END
from managers.result_manager import ResultManager
from utils.general_utils import generate_hash, to_timestamp_1dec
from models.audio_source import AudioSource
from models.audio_file import TextAudioFile
from models.result_row import ResultRow

class InteractiveTextManager():
    def __init__(self, result_manager, audio_load_callback) -> None:
        self.textbox : CTkTextbox = None
        self.selected_tag = None
        self.audio_load_callback = audio_load_callback
        self.result_manager : ResultManager = result_manager
    
        self.hovered_timestamp = " "

    def on_sentence_click(self):
        if self.selected_tag != None:
            self.textbox.tag_config(self.selected_tag, background="")

    def on_sentence_double_click(self, tag, result : ResultRow):
        if self.selected_tag != None:
            self.textbox.tag_config(self.selected_tag, background="")
        self.selected_tag = tag
        self.textbox.tag_config(tag, background="#999999")
        self.audio_load_callback(AudioSource.PREVIEWTEXT, TextAudioFile(result))

    def on_hover_enter(self, tag, result : ResultRow):
        self.textbox.tag_config(tag, background="#999999")
        self.textbox.configure(cursor="arrow")
        self.hovered_timestamp = to_timestamp_1dec(result.absolute_timestamp[0])

    def on_hover_leave(self, tag, result : ResultRow):
        if tag != self.selected_tag:
            self.textbox.tag_config(tag, background="")
        self.textbox.configure(cursor="xterm")
        self.hovered_timestamp = " "

    def get_timestamp(self):
        return self.hovered_timestamp
        

    def get_sentence_tag(self, result : ResultRow):
        return generate_hash(result.chunk_file + str(result.relative_timestamp))

    def refresh(self):
        self.textbox.configure(state='normal')
        self.textbox.delete("1.0", END)

        for result in self.result_manager.get():
            self.insert_text(result)

        self.textbox.configure(state='disabled')

    def insert_text(self, result : ResultRow):
        self.textbox.configure(state='normal')
        tag_name = self.get_sentence_tag(result)
        self.textbox.tag_bind(tag_name, "<Double-Button-1>", lambda e, tag=tag_name, result=result: self.on_sentence_double_click(tag, result))
        self.textbox.tag_bind(tag_name, "<Button-1>", lambda e: self.on_sentence_click())
        self.textbox.tag_bind(tag_name, "<Enter>", lambda e, tag=tag_name, result=result: self.on_hover_enter(tag, result))
        self.textbox.tag_bind(tag_name, "<Leave>", lambda e, tag=tag_name, result=result: self.on_hover_leave(tag, result))
        self.textbox.insert(END, result.sentence, tag_name)
        self.textbox.insert(END, " ")
        self.textbox.configure(state='disabled')

