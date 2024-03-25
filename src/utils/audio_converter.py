import os

audio_file_formats = [
    ("MP3 fájlok", "*.mp3"),
    ("WAV fájlok", "*.wav"),
    ("AAC fájlok", "*.aac"),
    ("FLAC fájlok", "*.flac"),
    ("ALAC fájlok", "*.m4a"),  # Note: ALAC files often use the .m4a extension
    ("OGG fájlok", "*.ogg"),
    ("WMA fájlok", "*.wma"),
    ("AC3 fájlok", "*.ac3"),
    ("DTS fájlok", "*.dts"),
    ("APE fájlok", "*.ape"),
    ("M4A fájlok", "*.m4a"),
    ("AIFF fájlok", "*.aiff"),
    ("Opus fájlok", "*.opus"),
    ("AMR fájlok", "*.amr"),
    ("RealAudio fájlok", "*.ra"),
    ("WAVPack fájlok", "*.wv"),
    ("MIDI fájlok", "*.midi"),
    ("PCM fájlok", "*.pcm"),
    ("AVI fájlok", "*.avi"),
    ("MKV fájlok", "*.mkv"),
    ("MP4 fájlok", "*.mp4"),
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
        import shutil
        from custom_pydub.utils import run_ffmpeg_command

        if self.__original_extension == '.wav':
            shutil.copy(self.__original_file_path, self.converted_audio_path)
        elif any(f'*{self.__original_extension}' == ext[1] for ext in audio_file_formats):
            command = ['ffmpeg',
                       '-i', self.__original_file_path,
                       '-vn', '-acodec', 'pcm_s16le', '-ac',
                       '2', '-ar', '44100', self.converted_audio_path]
            run_ffmpeg_command(command)
        else:
            raise Exception("A fájl formátuma nem támogatott!")

        self.converted_audio_duration = self.__get_wav_duration(
            self.converted_audio_path)

    def __get_wav_duration(self, wav_file_path: str) -> int:
        import wave

        with wave.open(wav_file_path, "r") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return int(round((frames / float(rate)) * 1000))
