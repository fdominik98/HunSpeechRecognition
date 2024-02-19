from threads.speech_base_thread import SpeechBaseThread
import os
from models.task import Task
from models.settings import Settings
from models.process_state import ProcessState
from models.audio_file import AudioFile
from queue import Queue
from time import sleep
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager
from utils.general_utils import run_ffmpeg_command

class Mp3SplitterThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, error_callback,
                  split_audio_manager, trimmed_audio_manager):
        super().__init__('Mp3SplitterThread', settings, error_callback)
        self.input_queue : Queue = Queue()
        self.output_queue : Queue = Queue()
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        if not os.path.exists(self.settings.project_audio_path):
            print(f"File {self.settings.project_audio_path} not found.")
            return
        
        while not self.stopped():
            if not self.input_queue.empty():
                task : Task = self.input_queue.get()
                self.split_audio(task)
            else:
                sleep(1)


    def split_audio(self, task : Task):
        if not os.path.exists(task.split_file_path) and not os.path.exists(task.trim_file_path):
            command = [
                'ffmpeg',
                '-i', self.settings.project_audio_path,
                '-ss', str(task.split_timestamp[0]),
                '-t', str(task.split_timestamp[1] - task.split_timestamp[0]),
                '-acodec', 'copy',
                task.split_file_path
            ]
            stdout, stderr = run_ffmpeg_command(command)
            print(f'{task.split_file_path} split successfully.') 

            split_audio_file = AudioFile(segment_number=task.segment_number, file_path=task.split_file_path,
                                          absolute_timestamp=task.split_timestamp)

            if self.split_audio_manager.save_audio_file(split_audio_file):
                self.split_audio_manager.insert_widget_queue.put(split_audio_file)
            sleep(0.5) 
        else:
            print(f'{task.split_file_path} already split. Skipping...')            

        if task.process_state == ProcessState.TRIMMING or task.process_state == ProcessState.GENERATING:
            self.output_queue.put(task) 

    
