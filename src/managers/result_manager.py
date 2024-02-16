import csv
import os
from threading import Lock
from models.result_row import ResultRow
from queue import Queue
from models.task import Task
from models.segment import Segment
from typing import Optional

class ResultManager():
    def __init__(self, project_folder) -> None:
        self.__file_path = f'{project_folder}/result.csv'
        self.__lock = Lock()
        self.__result_list : list[ResultRow] = []
        self.widget_queue : Queue = Queue()

    def __load(self):
        # Load CSV into a list of dictionaries
        with open(self.__file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            [self.__result_list.append(ResultRow.from_dict(row)) for row in reader]
            
            
    def save_results(self, segments : list[Segment], task : Task) -> list[ResultRow]:
        if len(segments) == 0:
            return []
        
        new_results : list[ResultRow] = []
        for segment in segments:
            if len(segment.text) == 0:
                continue
            result = ResultRow(self.size(), task.segment_number, task.trim_file_path, (segment.start, segment.end),
                    (task.trim_timestamp[0] + segment.start, task.trim_timestamp[0] + segment.end),
                        segment.text.strip(), self.get_sentence_pos(segment.text.strip()))
            self.__result_list.append(result)
            new_results.append(result)
        
        with self.__lock:
            with open(self.__file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=new_results[0].to_dict().keys())
                writer.writerows([result.to_dict() for result in new_results])
        return new_results


    def load(self):
        with self.__lock:
            if os.path.exists(self.__file_path):
                self.__load()
                return    
            # If the file does not exist, create an empty file with headers
            headers = ['id', 'chunk_id', 'chunk_file', 'relative_timestamp', 'absolute_timestamp', 'sentence', 'sentence_pos']  # Define your headers here
            with open(self.__file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()

    def get_all(self) -> list[ResultRow]:
        with self.__lock:
            return self.__result_list
        
    def get(self, index) -> ResultRow:
        with self.__lock:
            return self.__result_list[index]

    def next_segment_num(self):
        with self.__lock:
            if len(self.__result_list) == 0:
                return 0
            return self.__result_list[-1].chunk_id + 1
        
    def size(self):
        with self.__lock:
            return len(self.__result_list)
        

    def get_sentence_pos(self, text : str) -> tuple[int, int]:
        with self.__lock:
            start_pos = 0
            if not len(self.__result_list) == 0 :
                start_pos = self.__result_list[-1].sentence_pos[1] + 2
            end_pos = start_pos + len(text) - 1
            return (start_pos, end_pos)
