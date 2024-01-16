from customtkinter import CTkFrame, CTkLabel, CTkSlider
from CTkListbox import *
from utils.fonts import label_font
from models.settings import Settings
from models.audio_file import AudioFile
from models.audio_source import AudioSource
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, AudioFileManager

class AudioPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, settings,
                 split_audio_manager, trimmed_audio_manager, original_audio_manager,
                  load_audio_callback):
        super().__init__(parent)
        self.settings : Settings = settings
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager
        self.original_audio_manager : AudioFileManager = original_audio_manager
        self.load_audio_callback = load_audio_callback

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
        self.original_listbox = CTkListbox(self, command=lambda opt, src=AudioSource.ORIGINAL: self.load_file_into_player(opt, src), height=20)
        self.original_listbox.grid(row=7, column=0, padx=15, pady=(0, 10), sticky='nsew')

        self.split_label = CTkLabel(self, text="Szegmensek:", height=10, font=label_font())
        self.split_label.grid(row=8, column=0, padx=20, pady=(0,2), sticky='sw')
        self.split_listbox = CTkListbox(self, command=lambda opt, src=AudioSource.SPLITLIST: self.load_file_into_player(opt, src))
        self.split_listbox.grid(row=9, column=0, padx=15, pady=(0, 10), sticky='nsew')

        self.trim_label = CTkLabel(self, text="Vágott szegmensek:", height=10, font=label_font())
        self.trim_label.grid(row=10, column=0, padx=20, pady=(0,2), sticky='sw')
        self.trim_listbox = CTkListbox(self, command=lambda opt, src=AudioSource.TRIMLIST: self.load_file_into_player(opt, src))
        self.trim_listbox.grid(row=11, column=0, padx=15, pady=(0, 10), sticky='nsew')
  
        self.grid_columnconfigure(0, weight=1)   
        self.grid_rowconfigure(9, weight=1, minsize=200)
        self.grid_rowconfigure(11, weight=1, minsize=200)
        self.grid_rowconfigure(7, weight=1, minsize=20)

        self.update_listboxes()

    def load_file_into_player(self, selected_option : AudioFile, source : AudioSource):
        self.load_audio_callback(source, selected_option)

    def __on_noise_db_slider_change(self, value):
        self.noise_db_value_label.configure(text=f'{value:.1f} dB') 

    def __on_noise_dur_slider_change(self, value):
        self.noise_dur_value_label.configure(text=f'{value:.1f} másodperc') 

    def update_listboxes(self): 
        found = False     
        if not self.original_audio_manager.insert_widget_queue.empty():
            self.original_listbox.insert('END', self.original_audio_manager.insert_widget_queue.get())
            found=True  
        if not self.split_audio_manager.insert_widget_queue.empty():
            self.split_listbox.insert('END', self.split_audio_manager.insert_widget_queue.get())
            found=True
        if not self.split_audio_manager.delete_widget_queue.empty():
            self.split_listbox.delete(self.split_audio_manager.delete_widget_queue.get())
            found=True
        if not self.trimmed_audio_manager.insert_widget_queue.empty():
            self.trim_listbox.insert('END', self.trimmed_audio_manager.insert_widget_queue.get())
            found=True
        if found:
            self.after(20, self.update_listboxes) 
        else:
            self.after(300, self.update_listboxes) 


