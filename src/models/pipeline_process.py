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


def check_for_cuda():
    from torch import cuda
    try:
        print('There are %d GPU(s) available.' % cuda.device_count())
        if cuda.is_available():
            print('We will use the GPU:', cuda.get_device_name(0))
        else:
            print('No GPU available, using the CPU instead.')
    except:
        print('Cuda is probably not installed on the system.')


def load_model(download_conn, model_type, model_path):
    from utils.model_loader import check_internet, check_whisper_model
    import shutil
    from faster_whisper import download_model
    
    if check_whisper_model(model_type, model_path):
        return

    download_conn.send(ModelInitState.CHECKING_FOR_CONN)
    while not check_internet():
        download_conn.send(ModelInitState.NO_CONN)
        sleep(2)
    download_conn.send(ModelInitState.DOWNLOADING_MODEL)
    try:
        path = download_model(model_type, cache_dir=model_path)
    except Exception:
        shutil.rmtree(model_path)
        download_conn.send(ModelInitState.ERROR)


def do_process_file(download_conn, init_conn, input_queue: ProcessQueue, output_queue: ProcessQueue):
    from faster_whisper import WhisperModel
    from utils.model_loader import select_whisper_model_type_cpu

    #model_type, has_gpu = select_whisper_model_type_gpu()
    model_type = select_whisper_model_type_cpu()
    model_path = get_whisper_model_path()

    load_model(download_conn, model_type, model_path)
    download_conn.send(ModelInitState.MODEL_FOUND)

    # if has_gpu:
    #     check_for_cuda()

    num_producers = 3

    model: WhisperModel = WhisperModel(model_type, device='cpu',
                                       num_workers=num_producers, download_root=model_path)
                                       
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
