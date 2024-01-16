import subprocess
from mutagen.mp3 import MP3

def get_audio_duration(file_path):
    audio = MP3(file_path)        
    return float(audio.info.length) 

def run_ffmpeg_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = process.communicate()
    return output, error