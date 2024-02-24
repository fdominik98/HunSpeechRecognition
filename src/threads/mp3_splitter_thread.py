from time import sleep
from queue import Queue
from custom_pydub.custom_audio_segment import AudioSegment
from custom_pydub.utils import run_ffmpeg_command
from threads.speech_base_thread import SpeechBaseThread
from models.task import Task
from models.settings import Settings
from models.audio_file import AudioFile
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, MainAudioManager
from models.process_state import ProcessState

class Mp3SplitterThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, error_callback,
                  split_audio_manager, trimmed_audio_manager):
        super().__init__('Mp3SplitterThread', settings, error_callback)
        self.input_queue : Queue = Queue()
        self.output_queue : Queue = Queue()
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        if not MainAudioManager.exists(self.settings.project_audio_path):
            print(f"File {self.settings.project_audio_path} not found.")
            return
        
        while not self.stopped():
            if not self.input_queue.empty():
                existed = self.split_audio(self.input_queue.get())
                if not existed:
                    sleep(0.5)
            else:
                sleep(1)


    def split_audio(self, task : Task):
        existed = False
        if self.split_audio_manager.exists(task.split_file_path):
            print(f'{task.split_file_path} already split. Skipping...')  
            existed = True       
        else:
            command = [
                'ffmpeg',
                '-i', self.settings.project_audio_path,
                '-ss', str(task.split_timestamp[0]),
                '-t', str(task.split_timestamp[1] - task.split_timestamp[0]),
                '-acodec', 'copy',
                task.split_file_path
            ]
            run_ffmpeg_command(command=command)
            audio : AudioSegment = AudioSegment.from_mp3(task.split_file_path)
            audio = audio.set_channels(1)            
            audio = audio.apply_gain(0.0 - audio.max_dBFS)

            audio.export(task.split_file_path, format="mp3")
            split_audio_file = AudioFile(segment_number=task.segment_number,
                                        file_path=task.split_file_path,
                                        absolute_timestamp=task.split_timestamp)

            self.split_audio_manager.save_audio_file(split_audio_file)
            self.split_audio_manager.insert_widget_queue.put(split_audio_file)
            print(f'{task.split_file_path} split successfully.') 

        if not self.stopped() and (task.process_state is ProcessState.TRIMMING or task.process_state is ProcessState.GENERATING):
            self.output_queue.put(task) 
        return existed

    
