import os
from pydantic_yaml import YamlModel

EXEC_MODE = 'dev'


class Environment(YamlModel):
    cuda_path: str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.4'
    cuda_bin_path: str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.4/bin'
    cuda_libnvvp_path: str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.4/libnvvp'
    physx_path: str = 'C:/Program Files (x86)/NVIDIA Corporation/PhysX/Common'
    nvdlisr_path: str = 'C:/Program Files/NVIDIA Corporation/NVIDIA NvDLISR'
    cudnn_bin_path: str = '[INSTALL_DIR]/cudnn-windows-x86_64-8.9.7.29_cuda11-archive/bin'
    cudnn_bin_path2: str = '[INSTALL_DIR]/_internal/torch/lib'
    ffmpeg_path: str = '[INSTALL_DIR]/deploy/ffmpeg-master-latest-win64-gpl/bin'
    ffmpeg_path2: str = '[INSTALL_DIR]/ffmpeg-master-latest-win64-gpl/bin'

    last_project_dir: str = ''
    last_project_name: str = ''
    last_project_audio: str = ''
    
    recommended_model: str = ''


def get_root_path() -> str:
    try:
        if EXEC_MODE == 'dev':
            return os.environ['HUNSPEECH_DEV_PATH']
        elif EXEC_MODE == 'prod':
            return os.environ['HUNSPEECH_PATH']
        else:
            raise Exception('Hibás futtátasi mód. (Environment.py)')
    except:
        raise Exception(
            'A gyökér könyvtár nem található. Ellenőrizd a környezeti változókat.')


def get_app_data_path() -> str:
    try:
        if EXEC_MODE == 'dev':
            return os.environ['HUNSPEECH_DEV_PATH']
        elif EXEC_MODE == 'prod':
            return os.environ['HUNSPEECH_APPDATA']
        else:
            raise Exception('Hibás futtátasi mód. (Environment.py)')
    except:
        raise Exception(
            'A roaming data könyvtár nem található. Ellenőrizd a környezeti változókat, esetleg inditsd újra a számitógépet.')


def get_images_path() -> str:
    return f'{get_root_path()}/images'


def get_whisper_model_path() -> str:
    return f'{get_app_data_path()}/whisper_models'


def get_environment_folder_path() -> str:
    return f'{get_app_data_path()}/environment'


def get_environment_file_path() -> str:
    return f'{get_environment_folder_path()}/environment.yaml'


def get_log_folder_path() -> str:
    return f'{get_app_data_path()}/log'


def get_log_file_path() -> str:
    return f'{get_log_folder_path()}/output.log'


def add_to_path(path: str):
    current_path = os.environ.get('PATH', '')
    new_path = f"{current_path};{path}"
    os.environ['PATH'] = new_path
