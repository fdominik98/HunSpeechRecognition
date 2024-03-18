import os
import json
from typing import Optional
from abc import ABC
from models.audio_file import AudioFile, AudioSource
from managers.asset_tree_manager import AssetTreeManager
from managers.loadable_manager import LoadableManager
from models.result_row import ResultRow


class AudioFileManager(LoadableManager, ABC):
    def __init__(self, asset_folder: str, audio_source: AudioSource) -> None:
        super().__init__(audio_source)
        self._asset_folder = asset_folder
        self._path_list: list[str] = []
        self._size = 0

    @staticmethod
    def get_info_path(path: str) -> str:
        return f'{os.path.dirname(path)}/{os.path.basename(path).split(".")[0]}-info.json'

    def size(self) -> int:
        with self._lock:
            return self._size

    def delete_all(self):
        with self._lock:
            self._size = 0
            for root, dirs, files in os.walk(self._asset_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)

    def get_by_path(self, path: str) -> Optional[AudioFile]:
        with self._lock:
            if path not in self._path_list:
                return None
            return self.load_file(path)

    def get_by_index(self, index: int) -> Optional[AudioFile]:
        with self._lock:
            if index >= len(self._path_list) or index < 0:
                return None
            return self.load_file(self._path_list[index])

    def get_all(self) -> list[AudioFile]:
        with self._lock:
            res = []
            self._size = 0
            for path in self._path_list:
                file = self.load_file(path)
                if file is not None:
                    self._size += 1
                    res.append(file)
            return res

    @staticmethod
    def exists(path: str) -> bool:
        info_path = AudioFileManager.get_info_path(path)
        return os.path.isfile(path) and str(path).lower().endswith('.wav') and os.path.exists(info_path)

    def contains(self, path: str) -> bool:
        return self.exists(path) and path in self._path_list

    @staticmethod
    def load_file(file_path) -> Optional[AudioFile]:
        if AudioFileManager.exists(file_path):
            info_path = AudioFileManager.get_info_path(file_path)
            with open(info_path, 'r') as f:
                general_data = json.load(f)
            return AudioFile(general_data["chunk_id"],
                             file_path,
                             tuple(general_data["absolute_timestamp"]),
                             is_place_holder=general_data["is_place_holder"])
        return None

    def save_audio_file(self, audio_file: AudioFile):
        with self._lock:
            info_path = AudioFileManager.get_info_path(audio_file.file_path)
            data_to_store = {"chunk_id": audio_file.chunk_id,
                             "absolute_timestamp": audio_file.absolute_timestamp,
                             "is_place_holder": audio_file.is_place_holder}
            with open(info_path, 'w') as f:
                json.dump(data_to_store, f)
            self._size += 1

    def __delete_file_safe(self, file_path) -> bool:
        info_path = AudioFileManager.get_info_path(file_path)
        try:
            # Try to rename the file, which can fail if the file is in use
            temp_path = file_path + '.tmp'
            os.rename(file_path, temp_path)
            # If successful, delete the file
            os.remove(temp_path)

            temp_path = info_path + '.tmp'
            os.rename(info_path, temp_path)
            # If successful, delete the file
            os.remove(temp_path)

            return True
        except OSError as e:
            raise OSError(
                'A fájl nem törölhető mert használatban van. Próbáld leállítani a lejátszást és indítsd újra a műveletet!')

    def __do_delete_audio_file(self, path: str) -> Optional[int]:
        if path in self._path_list and self.exists(path):
            if self.__delete_file_safe(path):
                self._size -= 1
                return self._path_list.index(path)
        return None

    def delete_audio_file(self, audio_file: AudioFile) -> Optional[int]:
        with self._lock:
            return self.__do_delete_audio_file(audio_file.file_path)

    def delete_at_index(self, index: int) -> Optional[int]:
        with self._lock:
            if index >= len(self._path_list) or index < 0:
                return None
            return self.__do_delete_audio_file(self._path_list[index])

    def get_next(self, audio_file: AudioFile) -> Optional[AudioFile]:
        with self._lock:
            index = self._path_list.index(audio_file.file_path) + 1
            if index >= len(self._path_list) or index < 0:
                return None
            return self.load_file(self._path_list[index])

    def get_prev(self, audio_file: AudioFile) -> Optional[AudioFile]:
        with self._lock:
            index = self._path_list.index(audio_file.file_path) - 1
            if index >= len(self._path_list) or index < 0:
                return None
            return self.load_file(self._path_list[index])

    def get_audio_by_result(self, result: ResultRow) -> Optional[AudioFile]:
        with self._lock:
            return self.load_file(result.chunk_file)


class SplitAudioFileManager(AudioFileManager):
    def __init__(self, asset_manager: AssetTreeManager) -> None:
        super().__init__(asset_manager.split_folder, AudioSource.SPLITLIST)
        self.asset_manager: AssetTreeManager = asset_manager

    def load(self):
        self._path_list = [
            task.split_file_path for task in self.asset_manager.get()]


class TrimmedAudioFileManager(AudioFileManager):
    def __init__(self, asset_manager: AssetTreeManager) -> None:
        super().__init__(asset_manager.trim_folder, AudioSource.TRIMLIST)
        self.asset_manager: AssetTreeManager = asset_manager

    def load(self):
        self._path_list = [
            task.trim_file_path for task in self.asset_manager.get()]


class MainAudioManager(AudioFileManager):
    def __init__(self, audio_path: str) -> None:
        super().__init__(os.path.dirname(audio_path), AudioSource.ORIGINAL)
        self._audio_file = self.load_file(audio_path)

    def size(self) -> int:
        with self._lock:
            return 1

    def delete_all(self):
        pass

    def get_by_path(self, path: str) -> Optional[AudioFile]:
        with self._lock:
            return self._audio_file

    def get_by_index(self, index: int) -> Optional[AudioFile]:
        with self._lock:
            return self._audio_file

    def get_all(self) -> list[AudioFile]:
        with self._lock:
            return [self._audio_file]

    def delete_audio_file(self, audio_file: AudioFile) -> Optional[int]:
        pass

    def delete_at_index(self, index: int) -> Optional[int]:
        pass

    def get_next(self, audio_file: AudioFile) -> Optional[AudioFile]:
        return None

    def get_prev(self, audio_file: AudioFile) -> Optional[AudioFile]:
        return None
