from pydantic_yaml import YamlModel
from math import ceil

class Settings(YamlModel):
    chunk_size : int = 29
    mp3_file : str = ''
    mp3_duration : float = 0
    noise_treshold : int = -60
    silence_dur : float = 0.5
    project_folder : str = ''

    def chunk_count(self):
        result = self.mp3_duration / self.chunk_size
        return ceil(result)
