from threads.speech_base_thread import SpeechBaseThread
from models.settings import Settings
from models.process_state import ProcessState
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, AudioFileManager
from managers.result_manager import ResultManager

class InitManagerThread(SpeechBaseThread): 
    def __init__(self, settings : Settings, process_state : ProcessState, error_callback):
        super().__init__('InitManagerThread', settings, process_state, error_callback)
        self.result_manager = ResultManager(project_folder=self.settings.project_folder)
        self.split_audio_manager = SplitAudioFileManager(project_folder=self.settings.project_folder)
        self.trimmed_audio_manager = TrimmedAudioFileManager(project_folder=self.settings.project_folder)
        self.original_audio_manager = AudioFileManager(asset_folder=self.settings.project_folder)

    def do_run(self):
        self.result_manager.load()
        self.original_audio_manager.load()
        self.split_audio_manager.load()
        self.trimmed_audio_manager.load()

        for result in self.result_manager.get():
            self.result_manager.widget_queue.put(result)
        for audio_file in self.original_audio_manager.get():
            self.original_audio_manager.insert_widget_queue.put(audio_file)
        for audio_file in self.split_audio_manager.get():
            self.split_audio_manager.insert_widget_queue.put(audio_file)
        for audio_file in self.trimmed_audio_manager.get():
            self.trimmed_audio_manager.insert_widget_queue.put(audio_file)
