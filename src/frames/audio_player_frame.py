from customtkinter import CTkFrame, CTkButton, CTkSlider, CTkTextbox, CTkLabel, HORIZONTAL, VERTICAL, CTkImage, END
import pygame
from mutagen.mp3 import MP3
import time
from utils.general_utils import to_timestamp_sec, to_timestamp_1dec
from utils.fonts import label_font, button_font, textbox_font
import tktooltip
from PIL import Image
import os
from models.audio_source import AudioSource
from models.audio_file import AudioFile
from typing import Optional

class AudioPlayerFrame(CTkFrame):
    def __init__(self, parent : CTkFrame, row, column):
        super().__init__(parent, height=80)
        pygame.init()
        pygame.mixer.init()

        self.is_playing : bool = False
        self.start_time : Optional[float] = None
        self.mp3_file : Optional[str] = None
        self.duration : int = 0

        image_base_path = f'{os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}/images'
        self.play_icon = CTkImage(Image.open(f'{image_base_path}/play.png'), size=(25, 25))
        self.pause_icon = CTkImage(Image.open(f'{image_base_path}/pause.png'), size=(25, 25))
        self.stop_icon = CTkImage(Image.open(f'{image_base_path}/stop.png'), size=(25, 25))
        self.next_icon = CTkImage(Image.open(f'{image_base_path}/next.png'), size=(25, 25))
        self.previous_icon = CTkImage(Image.open(f'{image_base_path}/previous.png'), size=(25, 25))
        self.speaker_icon = CTkImage(Image.open(f'{image_base_path}/speaker.png'), size=(20, 20))

        self.grid(row=row, column=column, pady=5, sticky="ewsn")

        self.previous_button = CTkButton(self, text="", command=self.previous, font=button_font(), image=self.previous_icon, corner_radius=40, width=80)
        self.previous_button.grid(row=0, padx=(50, 2), pady=(25, 0), column=0)

        self.play_button = CTkButton(self, text="", command=self.play, font=button_font(), image=self.play_icon, corner_radius=40, width=80)
        self.play_button.grid(row=0, pady=(25, 0), padx=2, column=1)

        # self.pause_button = CTkButton(self, text="", command=self.pause, font=button_font(), image=pause, corner_radius=40, width=80)
        # self.pause_button.grid(row=0, pady=(25, 0), padx=2, column=2)

        self.stop_button = CTkButton(self, text="", command=self.stop, font=button_font(), image=self.stop_icon, corner_radius=40, width=80)
        self.stop_button.grid(row=0, pady=(25, 0), padx=2, column=2)

        self.next_button = CTkButton(self, text="", command=self.next, font=button_font(), image=self.next_icon, corner_radius=40, width=80)
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


    def on_nav_slider_hover(self, event):
        relative_position = event.x / self.navigation_slider.winfo_width()
        self.nav_slider_preview = self.duration * relative_position

    def on_volume_slider_hover(self, event):
        relative_position = 1 - (event.y / self.volume_slider.winfo_height())
        self.volume_slider_preview = 100 * relative_position


    def previous(self):
        self.stop()
        print('Not implemented!')
        pass
    def next(self):
        self.stop()
        print('Not implemented!')
        pass

    def get_nav_slider_preview(self):
        return to_timestamp_sec(self.nav_slider_preview)
    
    def get_volume_slider_preview(self):
        return int(round(self.volume_slider_preview))

    def play(self):
        if not self.loaded() :
            return
        if self.navigation_slider.get() == 100:
            self.pause()
            return
        pygame.mixer.music.play(start=self.navigation_slider.get() * self.duration / 100)
        self.is_playing = True
        self.start_time = time.time() - self.navigation_slider.get() * self.duration / 100
        self.update_slider_position()
        self.play_button.configure(image=self.pause_icon, command=self.pause)

    def pause(self):
        if not self.loaded() :
            return
        pygame.mixer.music.pause()
        self.is_playing = False
        self.play_button.configure(image=self.play_icon, command=self.play)

    def stop(self):
        if not self.loaded() :
            return
        pygame.mixer.music.stop()
        self.is_playing = False
        self.navigation_slider.set(0)
        self.end_time_label.configure(text=to_timestamp_sec(0))
        self.start_time_label.configure(text=to_timestamp_sec(0))
        pygame.mixer.music.unload()
        self.mp3_file = None

        self.audio_info_textbox.configure(state='normal')
        self.audio_info_textbox.delete("1.0", END)
        self.audio_info_textbox.configure(state='disabled')

        self.play_button.configure(image=self.play_icon, command=self.play)

    def adjust_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume) / 100)
        self.min_volume_label.configure(text=int(round(volume)))

    def navigate(self, val):
        if not self.loaded() :
            return
        
        timestamp = float(val) * self.duration / 100
        if pygame.mixer.music.get_busy():
            self.start_time = time.time() - timestamp  
            pygame.mixer.music.play(start=timestamp)
            if val == 100:
                self.pause()

    def update_duration(self):
        audio = MP3(self.mp3_file)
        self.duration = audio.info.length
        self.end_time_label.configure(text=to_timestamp_sec(self.duration)) 

    def update_slider_position(self):
        if not self.winfo_exists():
            return
        if self.is_playing:
            elapsed_time = time.time() - self.start_time
            self.navigation_slider.set(elapsed_time / self.duration * 100)
            self.start_time_label.configure(text=to_timestamp_sec(elapsed_time))
            if elapsed_time >= self.duration:
                self.pause()
                return
            self.after(50, self.update_slider_position)

    def load(self, source : AudioSource, audio_file : AudioFile):
        self.is_playing = False
        self.mp3_file = audio_file.file_path
        pygame.mixer.music.load(audio_file.file_path)

        if source == AudioSource.PREVIEWTEXT:
            start_time = audio_file.relative_timestamp[0]
        else:
            start_time = 0

        self.update_duration()
        self.navigation_slider.set(start_time / self.duration * 100)
        self.navigate(start_time)

        self.audio_info_textbox.configure(state='normal')
        self.audio_info_textbox.delete("1.0", END)
        self.audio_info_textbox.insert(END, f'- Forrás: {source.value}\n')
        self.audio_info_textbox.insert(END, f'- Fájl: {os.path.basename(audio_file.file_path)}\n')
        self.audio_info_textbox.insert(END, f'- Útvonal: {audio_file.file_path}\n')
        timestamp_str =f'{to_timestamp_sec(audio_file.absolute_timestamp[0])} - {to_timestamp_sec(audio_file.absolute_timestamp[1])}'
        self.audio_info_textbox.insert(END, f'- Szegmens pozíció: {timestamp_str}\n')
        self.audio_info_textbox.configure(state='disabled')

        self.play_button.configure(image=self.play_icon, command=self.play)


    def loaded(self):
        return self.mp3_file is not None

