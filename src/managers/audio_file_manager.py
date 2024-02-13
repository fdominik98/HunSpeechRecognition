from threading import Lock
from abc import ABC 
from models.audio_file import AudioFile
import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, COMM
from typing import Optional
from queue import Queue
from managers.asset_tree_manager import AssetTreeManager


class AudioFileManager(ABC):
    def __init__(self, asset_folder : str) -> None:        
        self.asset_folder = asset_folder
        self.__lock = Lock()
        self.__audio_file_list : list[AudioFile] = []
        self.insert_widget_queue : Queue = Queue()
        self.delete_widget_queue : Queue = Queue()

    def load(self):
        with self.__lock:
            if os.path.exists(self.asset_folder):
                self._load()
                return    
        os.makedirs(self.asset_folder)

    def _load_file(self, file_path):
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
                return
            # Deserialize the data
            data = json.loads(serialized_data)
            self.__audio_file_list.append(AudioFile(data["segment_number"],
                                            file_path,
                                            tuple(data["relative_timestamp"]),
                                            tuple(data["absolute_timestamp"])))

    def _load(self):
        for entry in os.listdir(self.asset_folder):
            file_path = f'{self.asset_folder}/{entry}'
            self._load_file(file_path)
                
    def save_audio_file(self, audio_file : AudioFile) -> bool:
        with self.__lock:
            if any([obj.segment_number == audio_file.segment_number for obj in self.__audio_file_list]):
                return False
            self.__audio_file_list.append(audio_file)
            audio = MP3(audio_file.file_path, ID3=ID3)
            try:
                audio.add_tags()
            except:
                pass
            data_to_store = json.dumps({"segment_number": audio_file.segment_number,
                                         "relative_timestamp": audio_file.relative_timestamp,
                                         "absolute_timestamp": audio_file.absolute_timestamp})
            audio.tags.add(COMM(encoding=3, lang='eng', desc='AudioInfo', text=data_to_store))
            audio.save()
            return True
        
    def __do_delete_audio_file(self, audio_file : AudioFile) -> Optional[int]:
        found_object = next((obj for obj in self.__audio_file_list if obj.segment_number == audio_file.segment_number), None)
        if found_object:
            self.delete_file_safe(found_object.file_path)
            index = self.__audio_file_list.index(found_object)
            self.__audio_file_list.remove(found_object)
            return index
        return None

    def delete_file_safe(self, file_path):
        try:
            # Try to rename the file, which can fail if the file is in use
            temp_path = file_path + '.tmp'
            os.rename(file_path, temp_path)
            # If successful, delete the file
            os.remove(temp_path)
        except OSError as e:
            raise OSError('A fájl nem törölhető mert használatban van. Próbáld leállítani a lejátszást és indítsd újra a műveletet!')

    def delete_audio_file(self, audio_file : AudioFile) -> Optional[int]:
        with self.__lock:
            return self.__do_delete_audio_file(audio_file)

    def delete_at_index(self, index : int) -> Optional[int]:
        if index > self.size()-1:
            return None
        with self.__lock:
            return self.__do_delete_audio_file(self.__audio_file_list[index])
                    
    def get(self) -> list[AudioFile]:
        with self.__lock:
            return self.__audio_file_list
        
    def size(self) -> int:
        with self.__lock:
            return len(self.__audio_file_list)
        
    def delete_all(self):
        for audio_file in self.get():
            self.__do_delete_audio_file(audio_file)
        


class SplitAudioFileManager(AudioFileManager):
    def __init__(self, asset_manager : AssetTreeManager) -> None:
        super().__init__(asset_manager.split_folder)
        self.asset_manager : AssetTreeManager = asset_manager

    def _load(self):
        for task in self.asset_manager.get():
            self._load_file(task.split_file_path)

class TrimmedAudioFileManager(AudioFileManager):
    def __init__(self, asset_manager : AssetTreeManager) -> None:
        super().__init__(asset_manager.trim_folder)
        self.asset_manager : AssetTreeManager = asset_manager

    def _load(self):
        for task in self.asset_manager.get():
            self._load_file(task.trim_file_path)