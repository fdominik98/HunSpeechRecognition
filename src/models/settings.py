from math import ceil
from pydantic_yaml import YamlModel

class Settings(YamlModel):
    chunk_size : int = 29
    project_audio_path : str = ''
    project_audio_duration : float = 0
    noise_treshold : int = -30
    silence_dur : float = 2
    project_dir : str = ''
    project_name : str = ''
    project_audio_name : str = ''
    trim_switch_var : bool = True
    player_volume : int = 50

    def chunk_count(self):
        result = self.project_audio_duration / self.chunk_size
        return ceil(result)
