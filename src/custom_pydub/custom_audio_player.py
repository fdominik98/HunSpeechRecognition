from typing import Optional
from audioplayer.audioplayer_windows import AudioPlayerWindows as AP
from managers.audio_file_manager import AudioFileManager
from models.audio_file import AudioFile
import time


class AudioPlayer(AP):
    def __init__(self, audio_file_manager: AudioFileManager, audio_file: AudioFile, start_volume: int):
        super().__init__(audio_file.file_path)
        self.is_playing: bool = False
        self.start_time: Optional[int] = None
        self.audio_file: AudioFile = audio_file
        self.audio_manager: AudioFileManager = audio_file_manager
        self._player = self.load_player()
        self.is_temporal_paused = False
        self.volume = start_volume

    def play(self, elapsed_time: int):
        self._do_setvolume(self._volume)
        self._mciSendString('play {} from {}'.format(self._alias, elapsed_time))

        self.set_start_time(elapsed_time)
        self.is_playing = True
        self.is_temporal_paused = False

    def pause(self):
        self.is_playing = False
        super().pause()

    def temporal_pause(self):
        self.is_temporal_paused = self.is_playing
        self.pause()

    def conditional_play(self, elapsed_time: int):
        if self.is_temporal_paused:
            self.play(elapsed_time)

    def stop(self):
        self.is_playing = False
        super().stop()

    def audio_length(self) -> int:
        return self.audio_file.length

    def get_elapsed_time(self, cursor_value: int) -> int:
        return int(round(cursor_value * self.audio_length() / 100.0))

    def set_start_time(self, elapsed_time : int):
        self.start_time = int(round(time.time() * 1000)) - elapsed_time
