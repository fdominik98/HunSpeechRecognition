import os
import time
from typing import Optional
from customtkinter import CTkFrame, CTkButton, CTkSlider, CTkTextbox, CTkLabel, HORIZONTAL, VERTICAL, CTkImage, END
import pygame
from PIL import Image
import tktooltip
from models.result_row import ResultRow
from utils.general_utils import to_timestamp_sec, timestamp_str
from models.environment import get_images_path
from utils.fonts import label_font, textbox_font
from utils.window_utils import open_plot
from models.audio_file import AudioFile, AudioSource
from models.settings import Settings
from managers.audio_file_manager import AudioFileManager

class AudioPlayerFrame(CTkFrame):
    def __init__(self, parent : CTkFrame, row, column, settings : Settings):
        super().__init__(parent, height=80)
        self.settings = settings
        self.refresh_cursor_position = None
        self.unselect_trimming_textbox = None
        self.unselect_splitting_textbox = None
        self.unselect_result_preview = None

        pygame.init()
        pygame.mixer.init()

        self.is_playing : bool = False
        self.start_time : Optional[float] = None
        self.audio_file : Optional[AudioFile] = None
        self.audio_manager : Optional[AudioFileManager] = None 

        image_base_path = get_images_path()
        self.play_icon = CTkImage(Image.open(f'{image_base_path}/play.png'), size=(25, 25))
        self.pause_icon = CTkImage(Image.open(f'{image_base_path}/pause.png'), size=(25, 25))
        self.stop_icon = CTkImage(Image.open(f'{image_base_path}/stop.png'), size=(25, 25))
        self.next_icon = CTkImage(Image.open(f'{image_base_path}/next.png'), size=(25, 25))
        self.previous_icon = CTkImage(Image.open(f'{image_base_path}/previous.png'), size=(25, 25))
        self.speaker_icon = CTkImage(Image.open(f'{image_base_path}/speaker.png'), size=(20, 20))
        self.no_speaker_icon = CTkImage(Image.open(f'{image_base_path}/no-sound.png'), size=(20, 20))
        self.eye_icon = CTkImage(Image.open(f'{image_base_path}/eye.png'), size=(20, 20))

        self.grid(row=row, column=column, pady=5, sticky="ews")

        self.previous_button = CTkButton(self, text="", command=self.previous, image=self.previous_icon, corner_radius=40, width=80)
        self.previous_button.grid(row=0, padx=(50, 2), pady=(25, 0), column=0)

        self.play_button = CTkButton(self, text="", command=self.play, image=self.play_icon, corner_radius=40, width=80)
        self.play_button.grid(row=0, pady=(25, 0), padx=2, column=1)

        self.stop_button = CTkButton(self, text="", command=self.stop, image=self.stop_icon, corner_radius=40, width=80)
        self.stop_button.grid(row=0, pady=(25, 0), padx=2, column=2)

        self.next_button = CTkButton(self, text="", command=self.next, image=self.next_icon, corner_radius=40, width=80)
        self.next_button.grid(row=0, pady=(25, 0), padx=(2, 50), column=3)


        self.navigation_slider = CTkSlider(self, from_=0, to=100, orientation=HORIZONTAL, command=self.navigate)
        self.navigation_slider.set(0)
        self.nav_slider_preview = 0
        self.navigation_slider.grid(row=1, columnspan=4, padx=(20, 0), pady=(10, 10), sticky="ewn")
        self.navigation_slider.bind("<Motion>", self.on_nav_slider_hover)

        self.start_time_label = CTkLabel(self, text=to_timestamp_sec(0), height=10, font=label_font())
        self.start_time_label.grid(row=1, column=0, padx=(20, 0), pady=30, sticky='wn')

        self.end_time_label = CTkLabel(self, text=to_timestamp_sec(0), height=10, font=label_font())
        self.end_time_label.grid(row=1, column=3, sticky='en', pady=30)

        self.volume_slider = CTkSlider(self, from_=0, to=100, width=20, button_color='grey', orientation=VERTICAL, height=80, command=self.adjust_volume)
        self.volume_slider.set(50)  # Set the initial volume to 100%
        self.volume_slider_preview = 0
        self.volume_slider.grid(row=1, column=4, padx=(30, 10), pady=0, sticky="sn")
        self.volume_slider.bind("<Motion>", self.on_volume_slider_hover)


        self.max_volume_label = CTkLabel(self, text="100", height=10, font=label_font())
        self.max_volume_label.grid(row=0, column=4, pady=(15, 0), sticky='wes')

        self.min_volume_label = CTkLabel(self, text="0", height=10, font=label_font(), image=self.speaker_icon, compound='left', padx=10)
        self.min_volume_label.grid(row=2, column=4, pady=(0, 10), sticky='nw')

        self.min_volume_label.bind("<Button-1>", lambda e, vol=0: self.adjust_volume(vol))


        self.plot_button = CTkButton(self, text="", image=self.eye_icon, corner_radius=30, width=40, command=self.plot_amplitude)
        self.plot_button.grid(row=2, column=0, pady=(0, 10), padx=(20, 20), sticky='ws')


        self.audio_info_textbox = CTkTextbox(self, font=textbox_font(), wrap='none', height=120)
        self.audio_info_textbox.grid(row=0, rowspan=3, column=5, pady=(10, 10), padx=(20,10), sticky="wsne")
        self.audio_info_textbox.configure(state="disabled")

        self.volume_tooltip = tktooltip.ToolTip(self.volume_slider, msg=self.get_volume_slider_preview,
                                                delay=0.01, follow=True, refresh=0.3,
                                                fg="#ffffff", bg="black", padx=8, pady=8,
                                                font=label_font())
        self.navigation_tooltip = tktooltip.ToolTip(self.navigation_slider, msg=self.get_nav_slider_preview,
                                                delay=0.01, follow=True, refresh=0.3,
                                                fg="#ffffff", bg="black", padx=8, pady=8,
                                                font=label_font())

        self.grid_columnconfigure(5, weight=1)


    def is_init(self):
        return self.refresh_cursor_position and self.unselect_result_preview and self.unselect_splitting_textbox and self.unselect_trimming_textbox

    def on_nav_slider_hover(self, event):
        if not self.loaded():
            self.nav_slider_preview = 0
            return 
        relative_position = event.x / self.navigation_slider.winfo_width()
        self.nav_slider_preview = self.audio_file.length() * relative_position

    def on_volume_slider_hover(self, event):
        relative_position = 1 - (event.y / self.volume_slider.winfo_height())
        self.volume_slider_preview = 100 * relative_position

    def plot_amplitude(self):
        if not self.loaded() or not self.is_init() or self.audio_file.is_place_holder:
            return        
        open_plot(self.master, self.audio_file.file_path, self.audio_manager, self.audio_file)

    def previous(self):
        if not self.loaded() or not self.is_init():
            return
        
        manager = self.audio_manager
        prev_audio_file = self.audio_file
        audio_file = self.audio_manager.get_prev(self.audio_file)
        self.stop()
        if audio_file is not None:
            self.load(manager, audio_file)
        else:
            self.load(manager, prev_audio_file)

    def next(self):
        if not self.loaded() or not self.is_init():
            return
        
        manager = self.audio_manager
        prev_audio_file = self.audio_file
        audio_file = self.audio_manager.get_next(self.audio_file)
        self.stop()
        if audio_file is not None:
            self.load(manager, audio_file)
        else:
            self.load(manager, prev_audio_file)

    def get_nav_slider_preview(self):
        return to_timestamp_sec(self.nav_slider_preview)
    
    def get_volume_slider_preview(self):
        return int(round(self.volume_slider_preview))

    def play(self):
        if not self.loaded() or not self.is_init():
            return
        if self.navigation_slider.get() == 100:
            self.pause()
            return
        pygame.mixer.music.play(start=self.navigation_slider.get() * self.audio_file.length() / 100)
        self.is_playing = True
        self.start_time = time.time() - self.navigation_slider.get() * self.audio_file.length() / 100
        self.update_slider_position()
        self.play_button.configure(image=self.pause_icon, command=self.pause)

    def pause(self):
        if not self.loaded() :
            return
        pygame.mixer.music.pause()
        self.is_playing = False
        self.play_button.configure(image=self.play_icon, command=self.play)

    def stop(self):
        if not self.loaded() or not self.is_init():
            return
        self.unselect_trimming_textbox()
        self.unselect_splitting_textbox()
        self.unselect_result_preview()
        pygame.mixer.music.stop()
        self.is_playing = False
        self.navigation_slider.set(0)
        self.end_time_label.configure(text=to_timestamp_sec(0))
        self.start_time_label.configure(text=to_timestamp_sec(0))
        pygame.mixer.music.unload()
        self.audio_file = None
        self.audio_manager = None

        self.audio_info_textbox.configure(state='normal')
        self.audio_info_textbox.delete("1.0", END)
        self.audio_info_textbox.configure(state='disabled')

        self.play_button.configure(image=self.play_icon, command=self.play)

    def stop_if_loaded(self, audio_file : AudioFile):
        if self.audio_file and self.audio_manager and self.audio_manager.audio_source is AudioSource.SPLITLIST and audio_file.segment_number == self.audio_file.segment_number:
            self.stop()

    def adjust_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume) / 100)
        self.min_volume_label.configure(text=int(round(volume)))
        self.volume_slider.set(volume)
        if volume > 0:
            self.min_volume_label.configure(image=self.speaker_icon)
        else:
            self.min_volume_label.configure(image=self.no_speaker_icon)

    def navigate(self, val):
        if not self.loaded() :
            return
        
        timestamp = float(val) * self.audio_file.length() / 100
        if pygame.mixer.music.get_busy():
            self.start_time = time.time() - timestamp  
            pygame.mixer.music.play(start=timestamp)
            if val == 100:
                self.pause()

    def update_slider_position(self):
        if not self.winfo_exists() or not self.is_init():
            return
        
        elapsed_time = time.time() - self.start_time
        self.refresh_cursor_position(self.audio_file, elapsed_time)

        if self.is_playing:
            self.navigation_slider.set(elapsed_time / self.audio_file.length() * 100)
            self.start_time_label.configure(text=to_timestamp_sec(elapsed_time))
            if elapsed_time >= self.audio_file.length():
                self.pause()
                return
            self.after(50, self.update_slider_position)

    def load(self, file_manager : AudioFileManager, audio_file : Optional[AudioFile], result : Optional[ResultRow] = None):
        if not self.is_init():
            return
        
        if audio_file is None or not file_manager.exists(audio_file.file_path) or audio_file.is_place_holder:
            self.stop()
            return

        self.is_playing = False
        self.audio_file = audio_file
        self.audio_manager = file_manager
        pygame.mixer.music.load(audio_file.file_path)

        if result is not None:
            start_time = result.relative_timestamp[0]
        else:
            start_time = 0

        self.navigation_slider.set(start_time / self.audio_file.length() * 100)
        self.navigate(start_time)
        self.end_time_label.configure(text=to_timestamp_sec(self.audio_file.length())) 
        self.refresh_cursor_position(self.audio_file, start_time)

        self.audio_info_textbox.configure(state='normal')
        self.audio_info_textbox.delete("1.0", END)
        self.audio_info_textbox.insert(END, f'- Forrás: {self.audio_manager.audio_source.value}\n')
        self.audio_info_textbox.insert(END, f'- Fájl: {os.path.basename(audio_file.file_path)}\n')
        self.audio_info_textbox.insert(END, f'- Útvonal: {audio_file.file_path}\n')
        self.audio_info_textbox.insert(END, f'- Szegmens pozíció: {timestamp_str(audio_file.absolute_timestamp)}\n')

        if result is not None:
            self.audio_info_textbox.insert(END, f'\n- Szöveg pozíció: {timestamp_str(result.absolute_timestamp)}\n')

        self.audio_info_textbox.configure(state='disabled')
        self.play_button.configure(image=self.play_icon, command=self.play)


    def loaded(self):
        return self.audio_file is not None

