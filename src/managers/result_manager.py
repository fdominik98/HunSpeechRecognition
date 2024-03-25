import csv
import os
from typing import Optional
from models.result_row import ResultRow
from models.task import Task
from models.segment import Segment
from models.audio_file import AudioSource
from managers.loadable_manager import LoadableManager
from models.audio_file import AudioFile


class ResultManager(LoadableManager):
    def __init__(self, project_folder) -> None:
        super().__init__(AudioSource.PREVIEWTEXT)
        self.__file_path = f'{project_folder}/result.csv'
        self.__result_list: list[ResultRow] = []

    def save_results(self, segments: list[Segment], task: Task) -> list[ResultRow]:
        if len(segments) == 0:
            return []

        new_results: list[ResultRow] = []

        for segment in segments:
            current_start = segment.start

            if segment.end == None:
                #print(f'{task.chunk_id} {segment.start}-None": {segment.text.strip()}')
                current_end = task.get_audio_length()
            else:
                current_end = min(segment.end, task.get_audio_length())

            absolute_timestamp = (
                task.result_timestamp[0] + current_start, task.result_timestamp[0] + current_end)
            result = ResultRow(absolute_timestamp[0], task.chunk_id, task.result_file_path, (current_start, current_end),
                               absolute_timestamp, segment.text.strip())
            self.__result_list.append(result)
            new_results.append(result)

        with self._lock:
            self.__write_headers()
            with open(self.__file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(
                    file, fieldnames=new_results[0].to_dict().keys())
                writer.writerows([result.to_dict() for result in new_results])
        return new_results

    def load(self):
        with self._lock:
            self.__write_headers()
            with open(self.__file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                [self.__result_list.append(
                    ResultRow.from_dict(row)) for row in reader]

    def __write_headers(self):
        if os.path.exists(self.__file_path):
            return
        # If the file does not exist, create an empty file with headers
        headers = ['id', 'chunk_id', 'chunk_file', 'relative_timestamp',
                   'absolute_timestamp', 'sentence']  # Define your headers here
        with open(self.__file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

    def get_all(self) -> list[ResultRow]:
        with self._lock:
            return self.__result_list

    def get_by_id(self, id) -> Optional[ResultRow]:
        with self._lock:
            return next((item for item in self.__result_list if item.id == id), None)

    def chunk_size(self) -> int:
        with self._lock:
            unique_ids = set(res.chunk_id for res in self.__result_list)
            return len(unique_ids)

    def delete_all(self):
        with self._lock:
            if os.path.exists(self.__file_path):
                os.remove(self.__file_path)
            self.__result_list.clear()

    def get_result_by_audio(self, audio_file: AudioFile, elapsed_time: int) -> Optional[ResultRow]:
        with self._lock:
            return next((item for item in self.__result_list if
                         item.chunk_id == audio_file.chunk_id and
                         item.chunk_file == audio_file.file_path and
                         item.relative_timestamp[0] <= elapsed_time and
                         item.relative_timestamp[1] > elapsed_time), None)
