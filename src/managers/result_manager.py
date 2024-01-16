import csv
import os
from threading import Lock
from models.result_row import ResultRow
from queue import Queue

class ResultManager():
    def __init__(self, project_folder) -> None:
        self.__file_path = f'{project_folder}/result.csv'
        self.__lock = Lock()
        self.__result_list : list[ResultRow] = []
        self.widget_queue = Queue()

    def __load(self):
        # Load CSV into a list of dictionaries
        with open(self.__file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            [self.__result_list.append(ResultRow.from_dict(row)) for row in reader]
            
            
    def save_results(self, results : list[ResultRow]):
        if len(results) == 0:
            return
        
        with self.__lock:
            self.__result_list += results
            with open(self.__file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=results[0].to_dict().keys())
                writer.writerows([result.to_dict() for result in results])


    def load(self):
        with self.__lock:
            if os.path.exists(self.__file_path):
                self.__load()
                return    
            # If the file does not exist, create an empty file with headers
            headers = ['chunk_id', 'chunk_file', 'relative_timestamp', 'absolute_timestamp', 'sentence']  # Define your headers here
            with open(self.__file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()

    def get(self) -> list[ResultRow]:
        with self.__lock:
            return self.__result_list

    def size(self):
        if len(self.get()) == 0:
            return 0
        return self.get()[-1].chunk_id + 1