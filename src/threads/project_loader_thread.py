from threads.speech_base_thread import SpeechBaseThread
from utils.audio_converter import AudioConverter
from managers.settings_manager import SettingsManager
from managers.audio_file_manager import MainAudioManager
from models.audio_file import AudioFile
from managers.environment_manager import EnvironmentManager

class ProjectLoaderThread(SpeechBaseThread):
    def __init__(self, error_callback, environment_manager : EnvironmentManager, project_dir : str):
        self.settings_manager = SettingsManager(project_dir)
        super().__init__('ProjectLoaderThread', self.settings_manager.get(), error_callback)
        self.project_dir = project_dir
        self.environment_manager = environment_manager
        self.main_app_window = None

    def do_run(self):
        self.environment_manager.set_last_project_dir(self.settings.project_dir)
        self.environment_manager.set_last_project_name(self.settings.project_name)
        self.environment_manager.set_last_project_audio(self.settings.project_audio_path)
        self.environment_manager.save_environment()        


class ProjectCreatorThread(ProjectLoaderThread): 
    def __init__(self, error_callback, environment_manager : EnvironmentManager, project_dir : str, file_path : str, project_name : str):
        super().__init__(error_callback, environment_manager, project_dir)
        self.file_path = file_path
        self.project_name = project_name

    def do_run(self):
        audio_converter = AudioConverter(self.project_dir, self.file_path)
        audio_converter.convert_to_wav()

        audio_manager = MainAudioManager(audio_converter.converted_audio_path)
        audio_manager.save_audio_file(AudioFile(0, audio_converter.converted_audio_path, (0, audio_converter.converted_audio_duration)))

        with open(f'{self.project_dir}/.audiorecproj', 'w') as file:
            file.write('')

        self.settings.project_dir = self.project_dir
        self.settings.project_audio_path = audio_converter.converted_audio_path
        self.settings.project_audio_duration = audio_converter.converted_audio_duration
        self.settings.project_audio_name = audio_converter.converted_audio_name
        self.settings.project_name = self.project_name

        self.settings_manager.save_settings()

        super().do_run()


