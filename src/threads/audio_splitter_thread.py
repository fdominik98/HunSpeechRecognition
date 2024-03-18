from time import sleep
from queue import Queue
from custom_pydub.custom_audio_segment import AudioSegment
from custom_pydub.utils import run_ffmpeg_command
from threads.speech_base_thread import SpeechBaseThread
from models.task import Task
from models.settings import Settings
from models.audio_file import AudioFile
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, MainAudioManager
from models.progress_data import ProgressData


class AudioSplitterThread(SpeechBaseThread):
    def __init__(self, settings: Settings, error_callback, output_queue: Queue,
                 progress_data: ProgressData, split_audio_manager: SplitAudioFileManager,
                 trimmed_audio_manager: TrimmedAudioFileManager):
        super().__init__('AudioSplitterThread', settings, error_callback)
        self.input_queue: Queue = Queue()
        self.output_queue: Queue = output_queue
        self.progress_data: ProgressData = progress_data
        self.split_audio_manager: SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager: TrimmedAudioFileManager = trimmed_audio_manager

    def do_run(self):
        if not MainAudioManager.exists(self.settings.project_audio_path):
            print(f"File {self.settings.project_audio_path} not found.")
            return

        while not self.stopped():
            if not self.input_queue.empty():
                processed = self.split_audio(self.input_queue.get())
                self.progress_data.step_split_progress()
                if processed:
                    sleep(0.2)
            else:
                sleep(1)

    def split_audio(self, task: Task):
        processed = False
        if self.split_audio_manager.exists(task.split_file_path):
            print(f'{task.split_file_path} already split. Skipping...')
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
            audio: AudioSegment = AudioSegment.from_wav(task.split_file_path)
            audio = audio.apply_gain(-1.0 - audio.max_dBFS)

            audio.export(task.split_file_path, format="wav")

            split_audio_file = AudioFile(segment_number=task.chunk_id,
                                         file_path=task.split_file_path,
                                         absolute_timestamp=task.split_timestamp)

            self.split_audio_manager.save_audio_file(split_audio_file)
            self.split_audio_manager.insert_widget_queue.put(split_audio_file)
            print(f'{task.split_file_path} split successfully.')
            processed = True

        if not self.stopped():
            self.output_queue.put(task.set_result_timestamp(task.split_timestamp)
                                  .set_result_file_path(task.split_file_path))
        return processed
