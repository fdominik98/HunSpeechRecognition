from pydantic_yaml import YamlModel

class Environment(YamlModel):
    cuda_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3'
    cuda_bin_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3/bin'
    cuda_libnvvp_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3/libnvvp'
    cudnn_bin_path : str = 'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3/bin'
    physx_path : str = 'C:/Program Files (x86)/NVIDIA Corporation/PhysX/Common'
    nvdlisr_path : str = 'C:/Program Files/NVIDIA Corporation/NVIDIA NvDLISR'
    ffmpeg_path : str = 'C:/Users/freyd/Desktop/HunSpeechRecognition/ffmpeg-master-latest-win64-gpl/bin'


