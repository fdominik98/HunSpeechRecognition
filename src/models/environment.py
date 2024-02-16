from pydantic_yaml import YamlModel
import os

EXEC_MODE = 'dev'

class Environment(YamlModel):
    cuda_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3'
    cuda_bin_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3/bin'
    cuda_libnvvp_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3/libnvvp'
    physx_path : str = 'C:/Program Files (x86)/NVIDIA Corporation/PhysX/Common'
    nvdlisr_path : str = 'C:/Program Files/NVIDIA Corporation/NVIDIA NvDLISR'
    cudnn_bin_path : str = '[INSTALL_DIR]/deploy/cudnn-windows-x86_64-8.9.6.50_cuda12-archive/bin'
    cudnn_bin_path2 : str = '[INSTALL_DIR]/_internal/torch/lib'
    ffmpeg_path : str = '[INSTALL_DIR]/deploy/ffmpeg-master-latest-win64-gpl/bin'
    ffmpeg_path2 : str = '[INSTALL_DIR]/ffmpeg-master-latest-win64-gpl/bin'

def get_root_path() -> str:
    try:
        if EXEC_MODE == 'dev':
            return os.environ['HUNSPEECH_DEV_PATH']
        elif EXEC_MODE == 'prod':
            return os.environ['HUNSPEECH_PATH']
        else:
            raise Exception('Hibás futtátasi mód. (Environment.py)')
    except:
        raise Exception('A gyökér könyvtár nem található. Ellenőrizd a környezeti változókat.')
    
def add_to_path(path : str):
    current_path = os.environ.get('PATH', '')
    new_path = f"{current_path};{path}"
    os.environ['PATH'] = new_path


