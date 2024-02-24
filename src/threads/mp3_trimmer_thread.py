from time import sleep
from queue import Queue
from custom_pydub.custom_audio_segment import AudioSegment
from custom_pydub.silence import split_on_silence
from threads.speech_base_thread import SpeechBaseThread
from models.task import Task
from models.audio_file import AudioFile
from models.settings import Settings
from models.process_state import ProcessState
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager


class Mp3TrimmerThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, error_callback,
                  input_queue, output_queue, split_audio_manager, trimmed_audio_manager, audio_stop_callback):
        super().__init__('Mp3TrimmerThread', settings, error_callback)
        self.input_queue : Queue = input_queue
        self.output_queue : Queue = output_queue
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager
        self.audio_stop_callback = audio_stop_callback

    def do_run(self):
        while not self.stopped():
            if not self.input_queue.empty():        
                existed = self.process_file(self.input_queue.get())
                if not existed:
                    sleep(0.5)  
            else:
                sleep(1)


    def process_file(self, task : Task):
        existed = False
        audiofile = self.trimmed_audio_manager.get_by_path(task.trim_file_path)
        if audiofile is not None:
            print(f'{task.trim_file_path} exists. Skipping...')
            existed = True
        elif self.split_audio_manager.exists(task.split_file_path):
            audiofile, audio = self.trim_audio(task)
            if self.stopped():
                return existed
            audio.export(task.trim_file_path, format="mp3")
            self.trimmed_audio_manager.save_audio_file(audiofile)
            self.trimmed_audio_manager.insert_widget_queue.put(audiofile)
            print(f'{task.split_file_path} trimmed successfully.')
        else:
            print(f'{task.split_file_path} does not exist, cannot trim.')
            return existed
        
        if not self.stopped() and task.process_state is ProcessState.GENERATING:
            self.output_queue.put(task.set_trim_timestamp(audiofile.absolute_timestamp).set_place_holder(audiofile.is_place_holder))
        return existed
            


    def trim_audio(self, task : Task) -> tuple[AudioFile, AudioSegment]:
        audio = AudioSegment.from_mp3(task.split_file_path)
        processed_audio, first_start, last_end = split_on_silence(self.settings, audio)

        new_timestamp = task.split_timestamp
        is_place_holder = False
        if first_start is not None and last_end is not None and len(processed_audio) > 300:
            if len(audio) != len(processed_audio):    
                new_timestamp = (task.split_timestamp[0] + float(first_start) / 1000,
                                 task.split_timestamp[0] +  float(last_end) / 1000)
        else:
            processed_audio = AudioSegment.silent(duration=50)
            is_place_holder = True

        audio_file = AudioFile(segment_number=task.segment_number,
                        file_path=task.trim_file_path,
                        absolute_timestamp=new_timestamp,
                        is_place_holder=is_place_holder)
        return (audio_file, processed_audio)


    