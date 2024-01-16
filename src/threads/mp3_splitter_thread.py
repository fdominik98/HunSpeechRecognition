from threads.speech_base_thread import SpeechBaseThread
import os
from utils.command_utils import run_ffmpeg_command
from models.task import Task
from models.settings import Settings
from models.process_state import ProcessState
from models.audio_file import AudioFile
from queue import Queue
from time import sleep
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager

class Mp3SplitterThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, process_state : ProcessState, error_callback, trimming_queue,
                  split_audio_manager, trimmed_audio_manager):
        super().__init__('Mp3SplitterThread', settings, process_state, error_callback)
        self.trimming_queue : Queue = trimming_queue
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        self.split_mp3()
        # Indicate the end of the queue  
        self.trimming_queue.put(None)      
        
    def split_mp3(self):
        """
        Splits an MP3 file into segments of a specified length using FFmpeg.

        :param file_path: Path to the input MP3 file.
        :param segment_length: Length of each segment in seconds.
        :return: None
        """
        if not os.path.exists(self.settings.mp3_file):
            print(f"File {self.settings.mp3_file} not found.")
            return

        # Split the file into segments
        start = 0
        segment_number = 0
        while start < self.settings.mp3_duration and not self.stopped():
            end = min(start + self.settings.chunk_size, self.settings.mp3_duration)

            base_name = os.path.basename(self.settings.mp3_file)
            file_name_without_extension = os.path.splitext(base_name)[0]

            split_output_file = f"{self.split_audio_manager.asset_folder}/{file_name_without_extension}_{segment_number:03d}.mp3"
            trim_output_file = f"{self.trimmed_audio_manager.asset_folder}/{file_name_without_extension}_{segment_number:03d}.mp3"

            relative_timestamp = (float(start), float(end))
            if not os.path.exists(split_output_file) and not os.path.exists(trim_output_file):
                command = [
                    'ffmpeg',
                    '-i', self.settings.mp3_file,
                    '-ss', str(start),
                    '-t', str(end - start),
                    '-acodec', 'copy',
                    split_output_file
                ]
                run_ffmpeg_command(command)
                split_audio_file = AudioFile(segment_number=segment_number, file_path=split_output_file,
                                            relative_timestamp=relative_timestamp, absolute_timestamp=relative_timestamp)

                if self.split_audio_manager.save_audio_file(split_audio_file):
                    self.split_audio_manager.insert_widget_queue.put(split_audio_file)
                sleep(0.5)            

            if self.process_state == ProcessState.TRIMMING or self.process_state == ProcessState.GENERATING:
                self.trimming_queue.put(Task(segment_number = segment_number, 
                                            main_file_path=self.settings.mp3_file,
                                            split_file_path=split_output_file,
                                            split_timestamp=relative_timestamp,
                                            trim_file_path=trim_output_file))            

            start += self.settings.chunk_size
            segment_number += 1


