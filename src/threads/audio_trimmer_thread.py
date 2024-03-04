from time import sleep
from queue import Queue
from custom_pydub.custom_audio_segment import AudioSegment
from custom_pydub.silence import split_on_silence
from threads.speech_base_thread import SpeechBaseThread
from models.task import Task
from models.audio_file import AudioFile
from models.settings import Settings
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager
from models.progress_data import ProgressData


class AudioTrimmerThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, error_callback,
                  input_queue : Queue, output_queue : Queue, split_audio_manager : SplitAudioFileManager,
                  trimmed_audio_manager : TrimmedAudioFileManager, progress_data : ProgressData):
        super().__init__('AudioTrimmerThread', settings, error_callback)
        self.input_queue : Queue = input_queue
        self.output_queue : Queue = output_queue
        self.progress_data : ProgressData = progress_data
        self.split_audio_manager : SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        while not self.stopped():
            if not self.input_queue.empty():        
                processed = self.process_file(self.input_queue.get())
                self.progress_data.step_trim_progress()
                if processed:
                    sleep(0.3)  
            else:
                sleep(1)


    def process_file(self, task : Task):
        processed = False
        audiofile = self.trimmed_audio_manager.get_by_path(task.trim_file_path)
        if audiofile is not None:
            print(f'{task.trim_file_path} exists. Skipping...')
        elif self.split_audio_manager.exists(task.split_file_path):
            audiofile, audio = self.trim_audio(task)
            if self.stopped():
                return processed
            audio.export(task.trim_file_path, format="wav")
            self.trimmed_audio_manager.save_audio_file(audiofile)
            self.trimmed_audio_manager.insert_widget_queue.put(audiofile)
            print(f'{task.split_file_path} trimmed successfully.')
            processed = True
        else:
            print(f'{task.split_file_path} does not exist, cannot trim.')
            return processed
        
        if not self.stopped():
            self.output_queue.put(task.set_result_timestamp(audiofile.absolute_timestamp)
                                  .set_result_file_path(audiofile.file_path)
                                  .set_place_holder(audiofile.is_place_holder))
        return processed
            


    def trim_audio(self, task : Task) -> tuple[AudioFile, AudioSegment]:
        audio = AudioSegment.from_wav(task.split_file_path)
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

        audio_file = AudioFile(segment_number=task.chunk_id,
                        file_path=task.trim_file_path,
                        absolute_timestamp=new_timestamp,
                        is_place_holder=is_place_holder)
        return (audio_file, processed_audio)


    