from threads.speech_base_thread import SpeechBaseThread
from models.settings import Settings
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, MainAudioManager
from managers.result_manager import ResultManager
from managers.asset_tree_manager import AssetTreeManager


class InitManagerThread(SpeechBaseThread):
    def __init__(self, settings: Settings, error_callback):
        super().__init__('InitManagerThread', settings, error_callback)

        self.asset_tree_manager = AssetTreeManager(settings=settings)
        self.result_manager = ResultManager(
            project_folder=self.settings.project_dir)
        self.split_audio_manager = SplitAudioFileManager(
            self.asset_tree_manager)
        self.trimmed_audio_manager = TrimmedAudioFileManager(
            self.asset_tree_manager)
        self.original_audio_manager = MainAudioManager(
            audio_path=settings.project_audio_path)

    def do_run(self):
        self.asset_tree_manager.load()
        self.result_manager.load()
        self.split_audio_manager.load()
        self.trimmed_audio_manager.load()

        for result in self.result_manager.get_all():
            self.result_manager.insert_widget_queue.put(result)
        self.original_audio_manager.insert_widget_queue.put(
            self.original_audio_manager.get_by_index(0))

        for audio_file in self.split_audio_manager.get_all():
            self.split_audio_manager.insert_widget_queue.put(audio_file)
        for audio_file in self.trimmed_audio_manager.get_all():
            self.trimmed_audio_manager.insert_widget_queue.put(audio_file)
