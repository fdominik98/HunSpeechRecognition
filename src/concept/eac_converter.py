import os
import ffmpeg

def convert_eac3_to_mp3(input_file, output_file):
    stream = ffmpeg.input(input_file)
    stream = ffmpeg.output(stream, output_file, acodec='mp3')
    ffmpeg.run(stream)
    

def get_file_path(filename):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Construct the full file path
    return f'{script_dir}\\{filename}'

def add_to_path(path : str):
    current_path = os.environ.get('PATH', '')
    new_path = f"{current_path};{path}"
    os.environ['PATH'] = new_path

# Example usage
input_file_path = get_file_path('silence_test.wav')
output_file_path = get_file_path('silence_test.mp3')

add_to_path('C:/Users/freyd/Desktop/HunSpeechRecognition/deploy/ffmpeg-master-latest-win64-gpl/bin')
convert_eac3_to_mp3(input_file_path, output_file_path)
