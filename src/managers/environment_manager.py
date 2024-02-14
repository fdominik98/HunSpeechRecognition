from threading import Lock
from models.environment import Environment
import os
from utils.general_utils import get_root_path, add_to_path

class EnvironmentManager():
    def __init__(self) -> None:
       self.__file_path = f'{get_root_path()}/dependencies/environment.yaml'
       self.__lock = Lock()
       self.__load_environment()

    def __load_environment(self):
        with self.__lock:
            if os.path.exists(self.__file_path):
                self.__environment : Environment = Environment.parse_file(self.__file_path)
            else:
                self.__environment : Environment = Environment()
                with open(self.__file_path, 'w') as file:
                    file.write(self.__environment.yaml())
                raise Exception('A környezeti változó függőségek nincsenek configurálva ([Telepitő mappa]/dependencies/environment.yaml)')
            
            add_to_path(self.__environment.cuda_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.cuda_bin_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.cuda_libnvvp_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.physx_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.nvdlisr_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.ffmpeg_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.ffmpeg_path2.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.cudnn_bin_path.replace('[INSTALL_DIR]', get_root_path()))
            add_to_path(self.__environment.cudnn_bin_path2.replace('[INSTALL_DIR]', get_root_path()))
            os.environ['CUDA_PATH'] = self.__environment.cuda_path.replace('[INSTALL_DIR]', get_root_path())
            

    def save_settings(self) -> None:
        with self.__lock:
            with open(self.__file_path, 'w') as file:
                file.write(self.__environment.yaml())

