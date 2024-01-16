from threads.speech_base_thread import SpeechBaseThread
import os
from utils.command_utils import run_ffmpeg_command
from models.task import Task
from models.audio_file import AudioFile
from models.settings import Settings
from models.process_state import ProcessState
from queue import Queue
from time import sleep
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager

class Mp3TrimmerThread(SpeechBaseThread): 

    def __init__(self, settings : Settings, process_state : ProcessState, error_callback, trimming_queue,
                  pipeline_queue, split_audio_manager, trimmed_audio_manager):
        super().__init__('Mp3TrimmerThread', settings, process_state, error_callback)
        self.trimming_queue : Queue = trimming_queue
        self.pipeline_queue : Queue = pipeline_queue
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        while True and not self.stopped():
            task = self.trimming_queue.get()
            if task is None:
                break  # Stop the consumer if None is received
            self.process_file(task)            
        self.pipeline_queue.put(None)


    def process_file(self, task : Task):
        task.set_trim_timestamp(task.split_timestamp)
        if not os.path.exists(task.trim_file_path) and os.path.exists(task.split_file_path) and os.path.getsize(task.split_file_path) > 0:
            self.remove_silence(task)
            sleep(0.5)          

        if self.process_state == ProcessState.GENERATING:
            self.pipeline_queue.put(task.set_trim_timestamp(task.split_timestamp))

        audiofile = AudioFile(segment_number=task.segment_number,
                               file_path=task.trim_file_path,
                               relative_timestamp=task.trim_timestamp,
                               absolute_timestamp=task.split_timestamp)
        
        if self.trimmed_audio_manager.save_audio_file(audiofile):
            self.trimmed_audio_manager.insert_widget_queue.put(audiofile)
        delete_index = self.split_audio_manager.delete_audio_file(audiofile)
        if delete_index != None:
            self.split_audio_manager.delete_widget_queue.put(delete_index)

    def remove_silence(self, task: Task):        
        command = [
            'ffmpeg',
            '-i', task.split_file_path,
            '-af', f'silenceremove=stop_periods=-1:stop_duration={self.settings.silence_dur}:stop_threshold={self.settings.noise_treshold}dB',
            task.trim_file_path
        ]  
        _, info = run_ffmpeg_command(command)
