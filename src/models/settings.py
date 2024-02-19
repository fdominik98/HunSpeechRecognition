from pydantic_yaml import YamlModel
from math import ceil

class Settings(YamlModel):
    chunk_size : int = 29
    project_audio_path : str = ''
    project_audio_duration : float = 0
    noise_treshold : int = -60
    silence_dur : float = 0.5
    project_dir : str = ''
    project_name : str = ''
    project_audio_name : str = ''

    def chunk_count(self):
        result = self.project_audio_duration / self.chunk_size
        return ceil(result)
