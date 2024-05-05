from threading import Lock
import json
import os
from models.settings import Settings
from models.task import Task
from models.enums.process_state import ProcessState


class AssetTreeManager():
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.assets_folder = f'{settings.project_dir}/assets'
        self.split_folder = f'{self.assets_folder}/split'
        self.trim_folder = f'{self.assets_folder}/trim'
        self.asset_tree_file = f'{self.assets_folder}/asset_tree.json'
        self.__lock = Lock()
        self.__task_list: list[Task] = []
        self.asset_tree: dict[int, tuple[str, int, int]] = {}

    def load(self):
        with self.__lock:
            if os.path.exists(self.asset_tree_file):
                with open(self.asset_tree_file, 'r', encoding='utf8') as f:
                    self.__compose_tasks(json.load(f))
                return
            if not os.path.exists(self.split_folder):
                os.makedirs(self.split_folder)
            if not os.path.exists(self.trim_folder):
                os.makedirs(self.trim_folder)
            self.asset_tree = self.__calculate_tree_structure()
            with open(self.asset_tree_file, 'w', encoding='utf8') as f:
                json.dump(self.asset_tree, f)
            self.__compose_tasks(self.asset_tree)

    def __calculate_tree_structure(self) -> dict[int, tuple[str, int, int]]:
        chunk_timestamps = self.__calculate_chunk_timestamps()
        n = len(chunk_timestamps)
        # Calculate the necessary depth of the tree
        depth = 0
        while 10 ** depth < n:
            depth += 1

        # Function to recursively build the tree and assign file paths
        def build_tree(node_id, current_depth, max_depth, file_counter=[0]) -> dict[int, tuple[str, int, int]]:
            file_paths = {}

            if current_depth == max_depth:
                for i in range(10):
                    if file_counter[0] >= n:
                        break
                    id = file_counter[0]
                    file_paths[id] = (f'{node_id}/szelet_{id:03d}.wav', chunk_timestamps[id][0], chunk_timestamps[id][1])
                    file_counter[0] += 1
                return file_paths

            for i in range(10):
                child_id = f"{node_id}/{i}" if node_id else str(i)
                file_paths.update(build_tree(
                    child_id, current_depth + 1, max_depth, file_counter))

                # Stop if all files have been placed
                if file_counter[0] >= n:
                    break

            return file_paths

        # Start building the tree from the root
        return build_tree('', 0, depth)
    
    
    def __calculate_chunk_timestamps(self) -> list[tuple[int, int]]:
        from custom_pydub.custom_audio_segment import AudioSegment
        from pydub.silence import detect_silence
        
        chunk_timestamps : list[tuple[int, int]]= []
        
        audio_segment : AudioSegment = AudioSegment.from_wav(self.settings.project_audio_path)
        audio_segment : AudioSegment = audio_segment.apply_gain(-1.0 - audio_segment.max_dBFS)
        audio_segment.export(self.settings.project_audio_path, format='wav')
        start = 0
        end = min(self.settings.max_chunk_size, self.settings.project_audio_duration)
        while start < self.settings.project_audio_duration:
            duration = end - start
            threshold_end = end - min(10 * 1000, duration)
            split_segment : AudioSegment = audio_segment[threshold_end:end]
            silent_ranges = detect_silence(split_segment, 400, split_segment.dBFS -5 , 20)
            if len(silent_ranges) != 0:
                s_range = max(silent_ranges, key=lambda obj: obj[1] - obj[0])
                end = threshold_end + int(round((s_range[0] + s_range[1])/2))
            chunk_timestamps.append((start, end))
            start = end
            end = min(self.settings.project_audio_duration, end + self.settings.max_chunk_size)
        return chunk_timestamps


    def __compose_tasks(self, asset_tree: dict[int, tuple[str, int, int]]):
        sorted_asset_tree = sorted(
            [(int(key), asset_tree[key][0], int(asset_tree[key][1]), int(asset_tree[key][2])) for key in asset_tree.keys()], key=lambda x: x[0])
        self.__task_list = []
        for segment_id, path, start, end in sorted_asset_tree:
            split_timestamp = (start, end)
            split_file_path = f'{self.split_folder}/{path}'
            split_file_dir = os.path.dirname(split_file_path)
            if not os.path.exists(split_file_dir):
                os.makedirs(split_file_dir)
            trim_file_path = f'{self.trim_folder}/{path}'
            trim_file_dir = os.path.dirname(trim_file_path)
            if not os.path.exists(trim_file_dir):
                os.makedirs(trim_file_dir)

            task: Task = Task(process_state=ProcessState.STOPPED,
                              segment_number=segment_id,
                              split_timestamp=split_timestamp,
                              split_file_path=split_file_path,
                              trim_file_path=trim_file_path)
            self.__task_list.append(task)

    def get(self) -> list[Task]:
        with self.__lock:
            return self.__task_list
        
    def chunk_count(self) -> int:
        with self.__lock:
            return len(self.__task_list)
