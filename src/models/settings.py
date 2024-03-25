from pydantic_yaml import YamlModel


class Settings(YamlModel):
    max_chunk_size: int = 29000
    chunk_count : int = 0
    project_audio_path: str = ''
    project_audio_duration: int = 0
    noise_threshold: int = -30
    silence_dur: int = 2000
    project_dir: str = ''
    project_name: str = ''
    project_audio_name: str = ''
    trim_switch_var: bool = False
    player_volume: int = 50
    trim_dbfs_auto: bool = True
