import os
from threading import Lock
from models.environment import Environment
from models.environment import get_root_path, add_to_path, get_environment_file_path, get_environment_folder_path


class EnvironmentManager():
    def __init__(self) -> None:
        self.__file_path = get_environment_file_path()
        self.__folder_path = get_environment_folder_path()
        self.__lock = Lock()
        self.__load_environment()

    def __load_environment(self):
        with self.__lock:
            if not os.path.exists(self.__folder_path):
                os.makedirs(self.__folder_path)
            if not os.path.exists(self.__file_path):     
                self.__environment: Environment = Environment()
                with open(self.__file_path, 'w', encoding='utf8') as file:
                    file.write(self.__environment.yaml())
            else:
                self.__environment: Environment = Environment.parse_file(
                        self.__file_path)
            root_path = get_root_path()

            add_to_path(self.__environment.cuda_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.cuda_bin_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.cuda_libnvvp_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.physx_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.nvdlisr_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.ffmpeg_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.ffmpeg_path2.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.cudnn_bin_path.replace(
                '[INSTALL_DIR]', root_path))
            add_to_path(self.__environment.cudnn_bin_path2.replace(
                '[INSTALL_DIR]', root_path))
            os.environ['CUDA_PATH'] = self.__environment.cuda_path.replace(
                '[INSTALL_DIR]', root_path)
            os.environ['FFMPEG_PATH'] = self.__environment.ffmpeg_path.replace(
                '[INSTALL_DIR]', root_path)

    def save_environment(self) -> None:
        with self.__lock:
            with open(self.__file_path, 'w', encoding='utf8') as file:
                file.write(self.__environment.yaml())

    def get_last_project_dir(self) -> str:
        with self.__lock:
            return self.__environment.last_project_dir

    def set_last_project_dir(self, data: str):
        with self.__lock:
            self.__environment.last_project_dir = data

    def get_last_project_name(self) -> str:
        with self.__lock:
            return self.__environment.last_project_name

    def set_last_project_name(self, data: str):
        with self.__lock:
            self.__environment.last_project_name = data

    def get_last_project_audio(self) -> str:
        with self.__lock:
            return self.__environment.last_project_audio

    def set_last_project_audio(self, data: str):
        with self.__lock:
            self.__environment.last_project_audio = data
            
    def get_recommended_model(self) -> str:
        with self.__lock:
            return self.__environment.recommended_model

    def set_recommended_model(self, data: str):
        with self.__lock:
            self.__environment.recommended_model = data
