import os
from customtkinter import CTkTextbox
import hashlib
from mutagen.mp3 import MP3
from subprocess import PIPE, Popen, STARTUPINFO, SW_HIDE, STARTF_USESHOWWINDOW

def get_audio_duration(file_path):
    audio = MP3(file_path)        
    return float(audio.info.length) 

def append_to_file_name(original_path, prefix):
    # Split the original path into directory and file name
    directory, old_file_name = os.path.split(original_path)

    # Replace the old file name with the new name
    new_path = f'{directory}/{prefix + old_file_name}'
    return new_path

def empty(text : str):
    return ''.join(text.split()) == ''


def get_text(textbox : CTkTextbox):
    return textbox.get('0.0', 'end').strip()


def generate_hash(input_string):
    # Create a new sha256 hash object
    hasher = hashlib.sha256()
    # Update the hash object with the bytes of the input string
    hasher.update(input_string.encode())
    # Return the hexadecimal digest of the hash
    return hasher.hexdigest()


def to_timestamp_sec(seconds):
    """
    Convert a float representing seconds into a hours:minutes:seconds format if more than an hour,
    otherwise minutes:seconds format.

    Args:
    seconds (float): The number of seconds.

    Returns:
    str: A string representing the time in hours:minutes:seconds format if more than an hour,
         otherwise in minutes:seconds format.
    """
    # Convert to integer to avoid fractional seconds
    total_seconds = int(round(seconds))

    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format the time including hours if more than an hour
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def to_timestamp_1dec(seconds):
    """
    Convert a float representing seconds into a hours:minutes:seconds format with seconds
    having one decimal place, if more than an hour; otherwise minutes:seconds format.

    Args:
    seconds (float): The number of seconds.

    Returns:
    str: A string representing the time in hours:minutes:seconds format with seconds
         up to one decimal place if more than an hour, otherwise in minutes:seconds format.
    """
    # Calculate hours, minutes, and remaining seconds
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    remaining_seconds = seconds % 60

    # Format the time with hours if more than an hour, and with one decimal place for seconds
    if hours > 0:
        return f"{hours}:{minutes:02d}:{remaining_seconds:04.1f}"
    else:
        return f"{minutes}:{remaining_seconds:04.1f}"
    
def run_ffmpeg_command(command):
    # Create a STARTUPINFO structure
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
    # Prevents the console window from being shown
    startupinfo.wShowWindow = SW_HIDE
    # Example of running a command without showing a console window
    process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, startupinfo=startupinfo)
    output, error = process.communicate()
    return output, error

def timestamp_str(timestamp: tuple[float, float]) -> str:
    return f'{to_timestamp_sec(timestamp[1])} - {to_timestamp_sec(timestamp[0])}'





   



