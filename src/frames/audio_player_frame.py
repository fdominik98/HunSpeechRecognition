import os
import time
from typing import Optional
from customtkinter import CTkFrame, CTkButton, CTkSlider, CTkTextbox, CTkLabel, HORIZONTAL, VERTICAL, CTkImage, END
import tktooltip
from models.result_row import ResultRow
from utils.general_utils import to_timestamp_sec, timestamp_str
from models.environment import get_images_path
from utils.fonts import label_font, textbox_font
from utils.window_utils import open_plot
from models.audio_file import AudioFile
from models.settings import Settings
from managers.audio_file_manager import AudioFileManager
from custom_pydub.custom_audio_player import AudioPlayer

class AudioPlayerFrame(CTkFrame):
    def __init__(self, parent : CTkFrame, row, column, settings : Settings):
        super().__init__(parent, height=80)
        self.settings = settings
        self.refresh_cursor_position_callbacks : list = []
        self.stop_playing_callbacks : list = []

        self.audio_player : Optional[AudioPlayer] = None

        from PIL import Image
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

        self.play_button = CTkButton(self, text="", command=self.on_play, image=self.play_icon, corner_radius=40, width=80)
        self.play_button.grid(row=0, pady=(25, 0), padx=2, column=1)

        self.stop_button = CTkButton(self, text="", command=self.on_stop, image=self.stop_icon, corner_radius=40, width=80)
        self.stop_button.grid(row=0, pady=(25, 0), padx=2, column=2)

        self.next_button = CTkButton(self, text="", command=self.next, image=self.next_icon, corner_radius=40, width=80)
        self.next_button.grid(row=0, pady=(25, 0), padx=(2, 50), column=3)


        self.navigation_slider = CTkSlider(self, from_=0, to=100, orientation=HORIZONTAL, command=self.navigate)
        self.navigation_slider.set(0)
        self.nav_slider_preview = 0
        self.navigation_slider.grid(row=1, columnspan=4, padx=(20, 0), pady=(10, 10), sticky="ewn")
        self.navigation_slider.bind("<Motion>", self.on_nav_slider_hover)
        self.navigation_slider.bind("<ButtonPress-1>", self.on_navigation_start)
        self.navigation_slider.bind("<ButtonRelease-1>", self.on_navigation_end)

        self.elapsed_time_label = CTkLabel(self, text=to_timestamp_sec(0), height=10, font=label_font())
        self.elapsed_time_label.grid(row=1, column=0, padx=(20, 0), pady=30, sticky='wn')

        self.end_time_label = CTkLabel(self, text=to_timestamp_sec(0), height=10, font=label_font())
        self.end_time_label.grid(row=1, column=3, sticky='en', pady=30)

        self.volume_slider = CTkSlider(self, from_=0, to=100, width=20, button_color='grey', orientation=VERTICAL, height=80, command=self.adjust_volume)
        self.volume_slider_preview = 0
        self.volume_slider.grid(row=1, column=4, padx=(30, 10), pady=0, sticky="sn")
        self.volume_slider.bind("<Motion>", self.on_volume_slider_hover)


        self.max_volume_label = CTkLabel(self, text="100", height=10, font=label_font())
        self.max_volume_label.grid(row=0, column=4, pady=(15, 0), sticky='wes')

        self.min_volume_label = CTkLabel(self, text="0", height=10, font=label_font(), image=self.speaker_icon, compound='left', padx=10)
        self.min_volume_label.grid(row=2, column=4, pady=(0, 10), sticky='nw')

        self.min_volume_label.bind("<Button-1>", lambda e, vol=0: self.adjust_volume(vol))
        self.adjust_volume(settings.player_volume)


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

    def on_nav_slider_hover(self, event):
        if not self.loaded():
            self.nav_slider_preview = 0
            return 
        relative_position = event.x / self.navigation_slider.winfo_width()
        self.nav_slider_preview = self.audio_player.audio_length() * relative_position

    def on_volume_slider_hover(self, event):
        relative_position = 1 - (event.y / self.volume_slider.winfo_height())
        self.volume_slider_preview = 100 * relative_position

    def plot_amplitude(self):
        if not self.loaded():
            return        
        open_plot(self.master, self.audio_player.audio_manager, self.audio_player.audio_file)

    def previous(self):
        if not self.loaded():
            return
        
        prev_audio_player = self.audio_player       
        new_audio_file = prev_audio_player.audio_manager.get_prev(self.audio_player.audio_file)
        self.on_stop()
        if new_audio_file is not None:
            self.load(prev_audio_player.audio_manager, new_audio_file)
        else:
            self.load(prev_audio_player.audio_manager, prev_audio_player.audio_file)

    def next(self):
        if not self.loaded():
            return
        
        prev_audio_player = self.audio_player       
        new_audio_file = prev_audio_player.audio_manager.get_next(self.audio_player.audio_file)
        self.on_stop()
        if new_audio_file is not None:
            self.load(prev_audio_player.audio_manager, new_audio_file)
        else:
            self.load(prev_audio_player.audio_manager, prev_audio_player.audio_file)

    def get_nav_slider_preview(self):
        return to_timestamp_sec(self.nav_slider_preview)
    
    def get_volume_slider_preview(self):
        return int(round(self.volume_slider_preview))

    def on_play(self):
        if not self.loaded():
            return
        if self.navigation_slider.get() == 100:
            self.audio_player.pause()
            return
        self.audio_player.play(int(round(self.navigation_slider.get() * self.audio_player.audio_length() / 100)))
        self.update_slider_position()
        self.play_button.configure(image=self.pause_icon, command=self.on_pause)

    def on_pause(self):
        if not self.loaded():
            return
        self.audio_player.pause()
        self.play_button.configure(image=self.play_icon, command=self.on_play)

    def on_stop(self):
        if not self.loaded():
            return
        for cb in self.stop_playing_callbacks:
            cb()
        self.audio_player.stop()
        self.audio_player = None

        self.navigation_slider.set(0)
        self.end_time_label.configure(text=to_timestamp_sec(0))
        self.elapsed_time_label.configure(text=to_timestamp_sec(0))

        self.audio_info_textbox.configure(state='normal')
        self.audio_info_textbox.delete("1.0", END)
        self.audio_info_textbox.configure(state='disabled')

        self.play_button.configure(image=self.play_icon, command=self.on_play)


    def adjust_volume(self, volume):
        volume = int(round(volume))
        if self.loaded():
            self.audio_player.volume = volume
        self.min_volume_label.configure(text=volume)
        self.volume_slider.set(volume)
        self.settings.player_volume = volume
        if volume > 0:
            self.min_volume_label.configure(image=self.speaker_icon)
        else:
            self.min_volume_label.configure(image=self.no_speaker_icon)

    def navigate(self, val):
        if not self.loaded():
            return        
        self.set_elapsed_time(self.audio_player.get_elapsed_time(val))
        
    def set_elapsed_time(self, elapsed_time):
        self.audio_player.set_start_time(elapsed_time)
        self.elapsed_time_label.configure(text=to_timestamp_sec(elapsed_time))
        self.refresh_cursor_position(elapsed_time)
        

    def on_navigation_start(self, event):
        self.audio_player.temporal_pause()

    def on_navigation_end(self, event):
        value = self.navigation_slider.get()
        elapsed_time = self.audio_player.get_elapsed_time(value)
        if value >= 100:
            self.on_pause()
        else:
            self.audio_player.conditional_play(elapsed_time)
            self.update_slider_position()

    def update_slider_position(self):
        if not self.winfo_exists():
            return

        if self.audio_player.is_playing:
            elapsed_time = int(round(time.time() * 1000)) - self.audio_player.start_time
            self.refresh_cursor_position(elapsed_time)
            self.navigation_slider.set(elapsed_time / self.audio_player.audio_length() * 100)
            self.elapsed_time_label.configure(text=to_timestamp_sec(elapsed_time))
            if elapsed_time >= self.audio_player.audio_length():
                self.on_pause()
                return
            self.after(50, self.update_slider_position)

    def load(self, file_manager : AudioFileManager, audio_file : AudioFile, result : Optional[ResultRow] = None):
        if not file_manager.exists(audio_file.file_path) or audio_file.is_place_holder:
            self.on_stop()
            return

        if self.audio_player is None or audio_file != self.audio_player.audio_file:
            self.audio_player = AudioPlayer(file_manager, audio_file, self.volume_slider.get())

        if result is not None:
            elapsed_time = result.relative_timestamp[0]
        else:
            elapsed_time = 0

        self.navigation_slider.set(float(elapsed_time) / audio_file.length * 100)
        self.set_elapsed_time(elapsed_time)

        self.end_time_label.configure(text=to_timestamp_sec(audio_file.length)) 
        self.audio_info_textbox.configure(state='normal')
        self.audio_info_textbox.delete("1.0", END)
        self.audio_info_textbox.insert(END, f'- Forrás: {file_manager.audio_source.value}\n')
        self.audio_info_textbox.insert(END, f'- Fájl: {os.path.basename(audio_file.file_path)}\n')
        self.audio_info_textbox.insert(END, f'- Útvonal: {audio_file.file_path}\n')
        self.audio_info_textbox.insert(END, f'- Szegmens pozíció: {timestamp_str(audio_file.absolute_timestamp)}\n')
        self.audio_info_textbox.insert(END, f'- Szegmens hossz: {to_timestamp_sec(audio_file.length)}\n')

        if result is not None:
            self.audio_info_textbox.insert(END, f'\n- Szöveg pozíció: {timestamp_str(result.absolute_timestamp)}\n')
            self.audio_info_textbox.insert(END, f'- Szöveg hossz: {to_timestamp_sec(result.length)}\n')

        self.audio_info_textbox.configure(state='disabled')
        self.play_button.configure(image=self.play_icon, command=self.on_play)


    def loaded(self):
        return self.audio_player is not None
    
    def refresh_cursor_position(self, elapsed_time):
        for cb in self.refresh_cursor_position_callbacks:
            cb(self.audio_player.audio_file, elapsed_time)
            
    def on_trim_switch_flipped(self, switched):
        if not switched:
            self.on_stop()

