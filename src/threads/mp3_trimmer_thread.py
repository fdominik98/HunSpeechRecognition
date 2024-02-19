import os
from time import sleep
from queue import Queue
from utils.general_utils import run_ffmpeg_command
from threads.speech_base_thread import SpeechBaseThread
from models.task import Task
from models.audio_file import AudioFile
from models.settings import Settings
from models.process_state import ProcessState
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager


class Mp3TrimmerThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, error_callback,
                  input_queue, split_audio_manager, trimmed_audio_manager, audio_stop_callback):
        super().__init__('Mp3TrimmerThread', settings, error_callback)
        self.input_queue : Queue = input_queue
        self.output_queue : Queue = Queue()
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager
        self.audio_stop_callback = audio_stop_callback

    def do_run(self):
        while not self.stopped():
            if not self.input_queue.empty():        
                task = self.input_queue.get(timeout=1)
                self.process_file(task)
            else:
                sleep(1)


    def process_file(self, task : Task):
        if not os.path.exists(task.trim_file_path) and os.path.getsize(task.split_file_path) > 0:
            if os.path.exists(task.split_file_path):
                self.remove_silence(task)
                print(f'{task.split_file_path} trimmed successfully.')
                sleep(0.5)    
            else:
                print(f'{task.split_file_path} does not exist, cannot trim.')      
        else:
            print(f'{task.trim_file_path} exists or {task.split_file_path} is too small. Skipping...')

        if task.process_state == ProcessState.GENERATING:
            self.output_queue.put(task)

        audiofile = AudioFile(segment_number=task.segment_number,
                               file_path=task.trim_file_path,
                               absolute_timestamp=task.trim_timestamp)
        
        if self.trimmed_audio_manager.save_audio_file(audiofile):
            try:
                self.audio_stop_callback(audiofile)
                delete_index = self.split_audio_manager.delete_audio_file(audiofile)
            except Exception as e:
                self.trimmed_audio_manager.delete_audio_file(audiofile)
                raise e
            if delete_index is not None:
                self.trimmed_audio_manager.insert_widget_queue.put(audiofile)
                self.split_audio_manager.delete_widget_queue.put(delete_index)

    def remove_silence(self, task: Task):
        command = [
            'ffmpeg',
            '-i', task.split_file_path,
            '-af', f'silenceremove=start_duration=0.3:stop_periods=-1:stop_duration={self.settings.silence_dur}:stop_threshold={self.settings.noise_treshold}dB:timestamp=write',
            task.trim_file_path
        ]  
        stdout, stderr = run_ffmpeg_command(command)

