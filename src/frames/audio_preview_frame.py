from typing import Optional
from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkSlider, CTkButton
from utils.fonts import label_font, small_button_font
from models.settings import Settings
from models.audio_file import AudioFile
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, AudioFileManager
from models.process_state import ProcessState
from widgets.interactive_textbox import AudioInteractiveTextbox

class AudioPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, settings : Settings,
                 split_audio_manager : SplitAudioFileManager,
                 trimmed_audio_manager : TrimmedAudioFileManager,
                 original_audio_manager : AudioFileManager,
                 audio_load_callback, audio_play_callback, audio_stop_callback) -> None:
        super().__init__(parent)
        self.settings : Settings = settings
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager
        self.original_audio_manager : AudioFileManager = original_audio_manager

        self.audio_stop_callback = audio_stop_callback

        self.grid(row=row, column=column, sticky='nsew')
             
        self.noise_db_label = CTkLabel(self, text="Csend hangereje:", height=10, font=label_font())
        self.noise_db_label.grid(row=0, column=0, padx=20, pady=(10,0), sticky='nsew')
        # Create a Scale widget
        self.noise_db_slider = CTkSlider(self, from_=-60, to=0, command=self.__on_noise_db_slider_change)
        self.noise_db_slider.set(self.settings.noise_treshold)
        self.noise_db_slider.grid(row=1, column=0, padx=20, pady=0, sticky='nsew')

        self.noise_db_value_label = CTkLabel(self,
                                             text=f'{self.noise_db_slider.get():.1f} dB',
                                             height=10, font=label_font())
        self.noise_db_value_label.grid(row=2, column=0, padx=15, pady=0, sticky='nsew')


        self.noise_dur_label = CTkLabel(self, text="Csend időtartama:", height=10, font=label_font())
        self.noise_dur_label.grid(row=3, column=0, padx=20, pady=(10,0), sticky='nsew')
        # Create a Scale widget
        self.noise_dur_slider = CTkSlider(self, from_=0, to=5, command=self.__on_noise_dur_slider_change)
        self.noise_dur_slider.set(self.settings.silence_dur)
        self.noise_dur_slider.grid(row=4, column=0, padx=20, pady=0, sticky='nsew')

        self.noise_dur_value_label = CTkLabel(self,
                                              text=f'{self.noise_dur_slider.get():.1f} másodperc',
                                              height=10,
                                              font=label_font())
        self.noise_dur_value_label.grid(row=5, column=0, padx=15, pady=0, sticky='nsew')

        self.original_label = CTkLabel(self, text="Hangfájl:", height=10, font=label_font())
        self.original_label.grid(row=6, column=0, padx=20, pady=(30,2), sticky='sw')
        self.original_textbox = AudioInteractiveTextbox(self.original_audio_manager, audio_load_callback=audio_load_callback,
                                            audio_play_callback=audio_play_callback, master=self, height=20)
        self.original_textbox.grid(row=7, column=0, padx=15, pady=(0, 10), sticky='nsew')

        self.split_label = CTkLabel(self, text="Szegmensek:", height=10, font=label_font())
        self.split_label.grid(row=8, column=0, padx=(20, 0), pady=(0,2), sticky='sw')
        self.split_delete_button = CTkButton(self, fg_color="transparent", border_width=2, width=70, height=5, text_color=("gray10", "#DCE4EE")
                                                     ,command=self.__delete_splitted_content, text="töröl", font=small_button_font())
        self.split_delete_button.grid(row=8, column=0, padx=(0, 20), pady=(0,2), sticky="se")

        self.split_textbox = AudioInteractiveTextbox(self.split_audio_manager, audio_load_callback=audio_load_callback,
                                            audio_play_callback=audio_play_callback, master=self)
        self.split_textbox.grid(row=9, column=0, padx=15, pady=(0, 10), sticky='nsew')

        self.trim_label = CTkLabel(self, text="Vágott szegmensek:", height=10, font=label_font())
        self.trim_label.grid(row=10, column=0, padx=20, pady=(0,2), sticky='sw')
        self.trim_delete_button = CTkButton(self, fg_color="transparent", border_width=2, width=70, height=5, text_color=("gray10", "#DCE4EE")
                                                     ,command=self.__delete_trimmed_content, text="töröl", font=small_button_font())
        self.trim_delete_button.grid(row=10, column=0, padx=(0, 20), pady=(0,2), sticky="se")

        self.trim_textbox = AudioInteractiveTextbox(self.trimmed_audio_manager, audio_load_callback=audio_load_callback,
                                            audio_play_callback=audio_play_callback, master=self)
        self.trim_textbox.grid(row=11, column=0, padx=15, pady=(0, 10), sticky='nsew')
  
        self.grid_columnconfigure(0, weight=1)   
        self.grid_rowconfigure(9, weight=1, minsize=200)
        self.grid_rowconfigure(11, weight=1, minsize=200)
        self.grid_rowconfigure(7, weight=1, minsize=20)

        self.update_listboxes()

    def __delete_splitted_content(self):
        response = messagebox.askyesno("Törlés", "Biztos törlöd a vágatlan szegmenseket?")
        if response:
            self.audio_stop_callback()
            while self.split_audio_manager.size() > 0:
                delete_index : Optional[int] = self.split_audio_manager.delete_at_index(0)
                if delete_index is None:
                    return
                self.split_textbox.delete_row(delete_index + 1)
    
    def __delete_trimmed_content(self):
        response = messagebox.askyesno("Törlés", "Biztos törlöd a vágott szegmenseket?")
        if response:
            self.audio_stop_callback()
            while self.trimmed_audio_manager.size() > 0:
                delete_index : Optional[int] = self.trimmed_audio_manager.delete_at_index(0)
                if delete_index is None:
                    return
                self.trim_textbox.delete_row(delete_index + 1)


    def on_process_state_change(self, process_state : ProcessState, forced : bool):
        if process_state == ProcessState.STOPPED:
            self.split_delete_button.configure(state="normal")
            self.trim_delete_button.configure(state="normal")
        else:
            self.split_delete_button.configure(state="disabled")
            self.trim_delete_button.configure(state="disabled")

    def __on_noise_db_slider_change(self, value):
        self.noise_db_value_label.configure(text=f'{value:.1f} dB') 

    def __on_noise_dur_slider_change(self, value):
        self.noise_dur_value_label.configure(text=f'{value:.1f} másodperc') 

    def update_listboxes(self): 
        if not self.winfo_exists():
            return
        found = False     
        if not self.original_audio_manager.insert_widget_queue.empty():
            self.original_textbox.insert_row(-1, str(self.original_audio_manager.insert_widget_queue.get()))
            found=True  
        if not self.split_audio_manager.insert_widget_queue.empty():
            self.split_textbox.insert_row(-1, str(self.split_audio_manager.insert_widget_queue.get()))
            found=True
        if not self.split_audio_manager.delete_widget_queue.empty():
            self.split_textbox.delete_row(self.split_audio_manager.delete_widget_queue.get() + 1)
            found=True
        if not self.trimmed_audio_manager.insert_widget_queue.empty():
            self.trim_textbox.insert_row(-1, str(self.trimmed_audio_manager.insert_widget_queue.get()))
            found=True
        if found:
            self.after(0, self.update_listboxes) 
        else:
            self.after(300, self.update_listboxes) 


