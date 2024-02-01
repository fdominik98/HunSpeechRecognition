from threads.speech_base_thread import SpeechBaseThread
import os
from models.task import Task
from models.audio_file import AudioFile
from models.settings import Settings
from models.process_state import ProcessState
from queue import Queue
from time import sleep
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager
from utils.general_utils import run_ffmpeg_command


class Mp3TrimmerThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, error_callback,
                  input_queue, split_audio_manager, trimmed_audio_manager):
        super().__init__('Mp3TrimmerThread', settings, error_callback)
        self.input_queue : Queue = input_queue
        self.output_queue : Queue = Queue()
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        while not self.stopped():
            if not self.input_queue.empty():        
                task = self.input_queue.get(timeout=1)
                self.process_file(task)
            else:
                sleep(1)


    def process_file(self, task : Task):
        if not os.path.exists(task.trim_file_path) and os.path.exists(task.split_file_path) and os.path.getsize(task.split_file_path) > 0:
            self.remove_silence(task)
            sleep(0.5)          

        if task.process_state == ProcessState.GENERATING:
            self.output_queue.put(task)

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
            '-af', f'silenceremove=start_duration=0.3:stop_periods=-1:stop_duration={self.settings.silence_dur}:stop_threshold={self.settings.noise_treshold}dB:timestamp=write',
            task.trim_file_path
        ]  
        stdout, stderr = run_ffmpeg_command(command)
