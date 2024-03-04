from time import sleep
from multiprocessing import Queue as ProcessQueue, Pipe, Process
import psutil
from py3nvml.py3nvml import *
from torch import cuda 
from faster_whisper import WhisperModel
from models.task import Task
from threads.pipeline_producer_thread import PipelineProducerThread

class PipelineProcess(Process):
    def __init__(self) -> None:
        self.parent_conn, self.child_conn = Pipe()
        self.input_queue : ProcessQueue = ProcessQueue()
        self.output_queue : ProcessQueue = ProcessQueue()
        super().__init__(target=do_process_file, name="Pipeline process", args=(self.child_conn, self.input_queue, self.output_queue), daemon=True)

    def terminate(self) -> None:
        self.parent_conn.close()
        return super().terminate()


def check_gpu():
    try:
        nvmlInit()
        device_count = nvmlDeviceGetCount()
        if device_count > 0:
            handle = nvmlDeviceGetHandleByIndex(0)  # Assuming we're interested in the first GPU
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_gb = memory_info.total / (1024 ** 3)  # Convert bytes to GiB
            nvmlShutdown()
            return True, gpu_memory_gb
        else:
            return False, 0
    except NVMLError as e:
        print(f"Failed to access GPU information: {e}")
        return False, 0


def select_whisper_model():
    # Check system properties
    cpu_cores = psutil.cpu_count(logical=False)
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GiB
    has_gpu, gpu_memory_gb = check_gpu()

    print(f'CPU cores: {cpu_cores}')
    print(f'Total RAM (GB): {total_ram_gb}')
    print(f'GPU: {has_gpu}, GPU memory (GB): {gpu_memory_gb}')

    # Define thresholds for model selection
    ram_threshold_for_large = 16  # in GiB
    gpu_memory_threshold_for_large = 8  # in GiB

    if has_gpu and gpu_memory_gb >= gpu_memory_threshold_for_large and total_ram_gb >= ram_threshold_for_large:
        model = 'large'
    else:
        model = 'medium'

    print(f"Based on your system's resources, the recommended Whisper model to use is: {model}")
    return (model, has_gpu)

def check_for_cuda():
    try:
        print('There are %d GPU(s) available.' % cuda.device_count())
        if cuda.is_available():
            print('We will use the GPU:', cuda.get_device_name(0))
        else:
            print('No GPU available, using the CPU instead.')
    except:
        print('Cuda is probably not installed on the system.')


def do_process_file(conn, input_queue : ProcessQueue, output_queue: ProcessQueue):
    model_type, has_gpu = select_whisper_model()

    if has_gpu:
        check_for_cuda()

    num_producers = 3

    model : WhisperModel = WhisperModel(model_type, device='auto', num_workers=num_producers)
    conn.send('init_finished')

    producers : list[PipelineProducerThread] = []
    for id in range(num_producers):
        producer = PipelineProducerThread(id, model, output_queue)
        producers.append(producer)
        producer.start()
        
    
    while(True):
        task : Task = input_queue.get()
        while not any(producer.is_free() for producer in producers):
            sleep(1)
        for producer in producers:
            if producer.is_free():
                producer.input_queue.put(task)
                break








