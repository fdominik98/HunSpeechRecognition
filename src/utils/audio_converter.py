import os
import shutil
import wave
from custom_pydub.utils import run_ffmpeg_command

audio_file_formats = [
    ("MP3 files", "*.mp3"),
    ("WAV files", "*.wav"),
    ("AAC files", "*.aac"),
    ("FLAC files", "*.flac"),
    ("ALAC files", "*.m4a"), # Note: ALAC files often use the .m4a extension
    ("OGG files", "*.ogg"),
    ("WMA files", "*.wma"),
    ("AC3 files", "*.ac3"),
    ("DTS files", "*.dts"),
    ("APE files", "*.ape"),
    ("M4A files", "*.m4a"),
    ("AIFF files", "*.aiff"),
    ("Opus files", "*.opus"),
    ("AMR files", "*.amr"),
    ("RealAudio files", "*.ra"),
    ("WAVPack files", "*.wv"),
    ("MIDI files", "*.midi"),
    ("PCM files", "*.pcm"),
]

class AudioConverter():
    def __init__(self, project_folder_path, file_path) -> None:
        file_name, ext = os.path.splitext(os.path.basename(file_path))
        self.__original_extension = ext.lower()
        self.__original_file_path = file_path
        self.converted_audio_name = f'{file_name}.wav'
        self.converted_audio_path = f'{project_folder_path}/{self.converted_audio_name}'
        self.converted_audio_duration = 0
    
    def convert_to_wav(self):
        if self.__original_extension == '.wav':
            shutil.copy(self.__original_file_path, self.converted_audio_path)
        elif any(f'*{self.__original_extension}' == ext[1] for ext in audio_file_formats):
            command = ['ffmpeg',
                        '-i', self.__original_file_path, 
                        '-vn', '-acodec', 'pcm_s16le', '-ac',
                        '2', '-ar', '44100', self.converted_audio_path]
            run_ffmpeg_command(command)
        elif self.__original_extension == '.avi':
            raise Exception("A fájl formtuma nem támogatott!")
        elif self.__original_extension == '.mkv':
            raise Exception("A fájl formtuma nem támogatott!")
        else:
            raise Exception("A fájl formtuma nem támogatott!")

        self.converted_audio_duration = self.__get_wav_duration(self.converted_audio_path)
        

    def __get_wav_duration(self, wav_file_path : str) -> float:
        with wave.open(wav_file_path, "r") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return  frames / float(rate)
