from time import sleep
from multiprocessing import Queue as ProcessQueue, Pipe, Process
from models.task import Task
from threads.pipeline_producer_thread import PipelineProducerThread
from models.environment import get_whisper_model_path
from enum import Enum, unique


@unique
class ModelInitState(Enum):
    INIT_STARTED = 0
    CHECKING_FOR_MODEL = 1
    MODEL_FOUND = 2
    CHECKING_FOR_CONN = 3
    NO_CONN = 4
    DOWNLOADING_MODEL = 5
    INIT_FINISHED = 6
    ERROR = 7


class PipelineProcess(Process):
    def __init__(self) -> None:
        self.download_parent_conn, self.download_child_conn = Pipe()
        self.init_parent_conn, self.init_child_conn = Pipe()
        self.input_queue: ProcessQueue = ProcessQueue()
        self.output_queue: ProcessQueue = ProcessQueue()
        super().__init__(target=do_process_file, name="Pipeline process", args=(
            self.download_child_conn, self.init_child_conn, self.input_queue, self.output_queue), daemon=True)
        self.download_child_conn.send(ModelInitState.CHECKING_FOR_MODEL)

    def terminate(self) -> None:
        self.init_parent_conn.close()
        self.download_parent_conn.close()
        return super().terminate()


def download_model(download_conn, model_type, model_path):
    from utils.model_loader import check_internet
    import shutil
    import whisper

    download_conn.send(ModelInitState.CHECKING_FOR_CONN)
    while not check_internet():
        download_conn.send(ModelInitState.NO_CONN)
        sleep(2)
    download_conn.send(ModelInitState.DOWNLOADING_MODEL)
    try:
        model = whisper.load_model(model_type, device='cpu', download_root=model_path)
    except Exception:
        shutil.rmtree(model_path)
        download_conn.send(ModelInitState.ERROR)
        
    return model


def do_process_file(download_conn, init_conn, input_queue: ProcessQueue, output_queue: ProcessQueue):
    from utils.model_loader import select_whisper_model_type_cpu, check_whisper_model
    
    num_producers = 1
    model_path = get_whisper_model_path()
    model_type = select_whisper_model_type_cpu()
    model_type = "large"

    if check_whisper_model(model_type, model_path):
        download_conn.send(ModelInitState.MODEL_FOUND)
        import whisper
        model = whisper.load_model(model_type, device='cpu', download_root=model_path)  
    else:
        model = download_model(download_conn, model_type, model_path)
        download_conn.send(ModelInitState.MODEL_FOUND)
    
    init_conn.send(ModelInitState.INIT_FINISHED)

    producers: list[PipelineProducerThread] = []
    for id in range(num_producers):
        producer = PipelineProducerThread(id, model, output_queue)
        producers.append(producer)
        producer.start()

    while (True):
        task: Task = input_queue.get()
        while not any(producer.is_free() for producer in producers):
            sleep(1)
        for producer in producers:
            if producer.is_free():
                producer.input_queue.put(task)
                break
