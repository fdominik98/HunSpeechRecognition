import ffmpeg
import os

def convert_eac3_to_mp3(input_file, output_file):
    stream = ffmpeg.input(input_file)
    stream = ffmpeg.output(stream, output_file, acodec='mp3')
    ffmpeg.run(stream)

def get_file_path(filename):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Construct the full file path
    return f'{script_dir}/{filename}'

# Example usage
input_file_path = get_file_path('proba3.aac')
output_file_path = get_file_path('proba3.mp3')

convert_eac3_to_mp3(input_file_path, output_file_path)