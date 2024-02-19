from threading import Lock
import json
import os
from models.settings import Settings
from models.task import Task
from models.process_state import ProcessState

class AssetTreeManager():
    def __init__(self, settings : Settings) -> None:
        self.settings = settings
        self.assets_folder = f'{settings.project_dir}/assets'
        self.split_folder = f'{self.assets_folder}/split'
        self.trim_folder = f'{self.assets_folder}/trim'
        self.asset_tree_file = f'{self.assets_folder}/asset_tree.json'
        self.__lock = Lock()
        self.__task_list : list[Task] = []
        self.asset_tree : dict[int. str] = {}

    def load(self):
        with self.__lock:
            if os.path.exists(self.asset_tree_file):
                with open(self.asset_tree_file, 'r') as f:
                    self.__compose_tasks(json.load(f))
                return
            if not os.path.exists(self.split_folder):
                os.makedirs(self.split_folder)
            if not os.path.exists(self.trim_folder):
                os.makedirs(self.trim_folder)
            self.asset_tree = self.__calculate_tree_structure()
            with open(self.asset_tree_file, 'w') as f:
                json.dump(self.asset_tree, f)
            self.__compose_tasks(self.asset_tree)

        
    def __calculate_tree_structure(self) -> dict[int, str]:
        n = self.settings.chunk_count()
        # Calculate the necessary depth of the tree
        depth = 0
        while 10 ** depth < n:
            depth += 1

        # Function to recursively build the tree and assign file paths
        def build_tree(node_id, current_depth, max_depth, file_counter=[0]) -> dict[int, str]:
            file_paths = {}

            if current_depth == max_depth:
                for i in range(10):
                    if file_counter[0] >= n:
                        break
                    file_paths[file_counter[0]] = f'{node_id}/audio{file_counter[0]:03d}.mp3'
                    file_counter[0] += 1
                return file_paths

            for i in range(10):
                child_id = f"{node_id}/{i}" if node_id else str(i)
                file_paths.update(build_tree(child_id, current_depth + 1, max_depth, file_counter))

                # Stop if all files have been placed
                if file_counter[0] >= n:
                    break

            return file_paths

        # Start building the tree from the root
        return build_tree('', 0, depth)
    

    def __compose_tasks(self, asset_tree : dict[int, str]):
        sorted_asset_tree = sorted([(int(key), asset_tree[key]) for key in asset_tree.keys()], key=lambda x: x[0])
        self.__task_list = []
        for segment_id, path in sorted_asset_tree:
            start = segment_id * self.settings.chunk_size
            split_timestamp = (float(start), float(min(start + self.settings.chunk_size, self.settings.project_audio_duration)))

            split_file_path = f'{self.split_folder}/{path}'
            split_file_dir = os.path.dirname(split_file_path)
            if not os.path.exists(split_file_dir):
                os.makedirs(split_file_dir)
            trim_file_path = f'{self.trim_folder}/{path}'
            trim_file_dir = os.path.dirname(trim_file_path)
            if not os.path.exists(trim_file_dir):
                os.makedirs(trim_file_dir)

            task : Task = Task(process_state=ProcessState.STOPPED,
                               segment_number = segment_id,
                               main_file_path=self.settings.project_audio_path,
                               split_timestamp = split_timestamp, 
                               trim_timestamp = split_timestamp,
                               trim_file_path=trim_file_path,
                               split_file_path=split_file_path)
            self.__task_list.append(task)

    def get(self) -> list[Task]:
        with self.__lock:
            return self.__task_list

