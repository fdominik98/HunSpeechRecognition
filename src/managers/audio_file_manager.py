from abc import ABC 
from models.audio_file import AudioFile, AudioSource
import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, COMM
from typing import Optional
from managers.asset_tree_manager import AssetTreeManager
from managers.loadable_manager import LoadableManager
from models.result_row import ResultRow


class AudioFileManager(LoadableManager, ABC):
    def __init__(self, asset_folder : str, audio_source : AudioSource = AudioSource.ORIGINAL) -> None: 
        super().__init__(audio_source)       
        self.asset_folder = asset_folder
        self._audio_file_list : list[AudioFile] = []

    def load(self):
        with self._lock:
            if os.path.exists(self.asset_folder):
                self._load()
                return    
        os.makedirs(self.asset_folder)

    def load_file(self, file_path) -> Optional[AudioFile]:
        if os.path.isfile(file_path) and str(file_path).lower().endswith('.mp3'):
            audio = MP3(file_path, ID3=ID3)

            serialized_data = None
            # Extract the data from the comments
            for tag in audio.tags.getall('COMM'):
                if tag.desc == 'AudioInfo':
                    serialized_data = tag.text[0]
                    break
            if serialized_data == None:
                print('Warning: No data found in one of the segments!')
                return None
            # Deserialize the data
            data = json.loads(serialized_data)
            return AudioFile(data["segment_number"],
                                file_path,
                                tuple(data["absolute_timestamp"]))
        return None

    def _load(self):
        for entry in os.listdir(self.asset_folder):
            file_path = f'{self.asset_folder}/{entry}'
            audio_file = self.load_file(file_path)
            if audio_file is not None:
                self._audio_file_list.append(audio_file)
                
    def save_audio_file(self, audio_file : AudioFile) -> bool:
        with self._lock:
            if any([obj.segment_number == audio_file.segment_number for obj in self._audio_file_list]):
                return False
            self._audio_file_list.append(audio_file)
            audio = MP3(audio_file.file_path, ID3=ID3)
            try:
                audio.add_tags()
            except:
                pass
            data_to_store = json.dumps({"segment_number": audio_file.segment_number,
                                         "absolute_timestamp": audio_file.absolute_timestamp})
            audio.tags.add(COMM(encoding=3, lang='eng', desc='AudioInfo', text=data_to_store))
            audio.save()
            return True
        
    def __do_delete_audio_file(self, audio_file : AudioFile) -> Optional[int]:
        found_object = next((obj for obj in self._audio_file_list if obj.segment_number == audio_file.segment_number), None)
        if found_object:
            self.__delete_file_safe(found_object.file_path)
            index = self._audio_file_list.index(found_object)
            self._audio_file_list.remove(found_object)
            return index
        return None

    def __delete_file_safe(self, file_path):
        try:
            # Try to rename the file, which can fail if the file is in use
            temp_path = file_path + '.tmp'
            os.rename(file_path, temp_path)
            # If successful, delete the file
            os.remove(temp_path)
        except OSError as e:
            raise OSError('A fájl nem törölhető mert használatban van. Próbáld leállítani a lejátszást és indítsd újra a műveletet!')

    def delete_audio_file(self, audio_file : AudioFile) -> Optional[int]:
        with self._lock:
            return self.__do_delete_audio_file(audio_file)

    def delete_at_index(self, index : int) -> Optional[int]:
        with self._lock:
            if index > len(self._audio_file_list)-1:
                return None
            return self.__do_delete_audio_file(self._audio_file_list[index])
                    
    def get_all(self) -> list[AudioFile]:
        with self._lock:
            return self._audio_file_list

    def get(self, index : int) -> AudioFile:
        with self._lock:
            return self._audio_file_list[index]
        
    def size(self) -> int:
        with self._lock:
            return len(self._audio_file_list)
        
    def delete_all(self):
        with self._lock:
            for audio_file in self._audio_file_list:
                self.__do_delete_audio_file(audio_file)

    def get_next(self, audio_file : AudioFile) -> Optional[AudioFile]:
        with self._lock:
            found_object = next((obj for obj in self._audio_file_list if obj.segment_number == audio_file.segment_number), None)
            if found_object is not None:
                index = self._audio_file_list.index(found_object)
                if len(self._audio_file_list) > index + 1:
                    return self._audio_file_list[index + 1]
                return self._audio_file_list[-1]
            return None
        
    def get_prev(self, audio_file : AudioFile) -> Optional[AudioFile]:
        with self._lock:
            found_object = next((obj for obj in self._audio_file_list if obj.segment_number == audio_file.segment_number), None)
            if found_object is not None:
                index = self._audio_file_list.index(found_object)
                if index - 1 >= 0:
                    return self._audio_file_list[index - 1]
                return self._audio_file_list[0]
            return None
        


class SplitAudioFileManager(AudioFileManager):
    def __init__(self, asset_manager : AssetTreeManager) -> None:
        super().__init__(asset_manager.split_folder, AudioSource.SPLITLIST)
        self.asset_manager : AssetTreeManager = asset_manager

    def _load(self):
        for task in self.asset_manager.get():
            audio_file = self.load_file(task.split_file_path)
            if audio_file is not None:
                self._audio_file_list.append(audio_file)

class TrimmedAudioFileManager(AudioFileManager):
    def __init__(self, asset_manager : AssetTreeManager) -> None:
        super().__init__(asset_manager.trim_folder, AudioSource.TRIMLIST)
        self.asset_manager : AssetTreeManager = asset_manager

    def _load(self):
        for task in self.asset_manager.get():
            audio_file = self.load_file(task.trim_file_path)
            if audio_file is not None:
                self._audio_file_list.append(audio_file)

    def get_audio_by_result(self, result : ResultRow) -> Optional[AudioFile]:
        with self._lock:
            return next((item for item in self._audio_file_list if 
                           item.segment_number == result.chunk_id), None)