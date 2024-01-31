from threading import Lock
from models.settings import Settings
import os

class SettingsManager():
    def __init__(self, project_folder) -> None:
       self.__file_path = f'{project_folder}/settings.yaml'
       self.__lock = Lock()
       self.__load_settings()

    def __load_settings(self):
        with self.__lock:
            if os.path.exists(self.__file_path):
                self.__settings = Settings.parse_file(self.__file_path)
                return
            self.__settings = Settings()
            with open(self.__file_path, 'w') as file:
                file.write(self.__settings.yaml())

    def save_settings(self) -> None:
        with self.__lock:
            with open(self.__file_path, 'w') as file:
                file.write(self.__settings.yaml())

    def get(self) -> Settings:
        with self.__lock:
            return self.__settings