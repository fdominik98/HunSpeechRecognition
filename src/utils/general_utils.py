from mutagen.mp3 import MP3
from customtkinter import CTkTextbox

def get_audio_duration(file_path):
    audio = MP3(file_path)        
    return float(audio.info.length) 

def empty(text : str):
    return ''.join(text.split()) == ''


def get_text(textbox : CTkTextbox):
    return textbox.get('0.0', 'end').strip()


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
    return f"{minutes}:{remaining_seconds:04.1f}"
    
def timestamp_str(timestamp: tuple[float, float]) -> str:
    return f'{to_timestamp_sec(timestamp[0])} - {to_timestamp_sec(timestamp[1])}'





   



