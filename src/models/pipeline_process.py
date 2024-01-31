from multiprocessing import Queue as ProcessQueue, Pipe, Process
import os
from models.task import Task
from faster_whisper import WhisperModel
from torch import cuda 
from threads.pipeline_producer_thread import PipelineProducerThread
from time import sleep

class PipelineProcess(Process):
    def __init__(self) -> None:
        self.parent_conn, self.child_conn = Pipe()
        self.input_queue : ProcessQueue = ProcessQueue()
        self.output_queue : ProcessQueue = ProcessQueue()
        super().__init__(target=do_process_file, name="Pipeline process", args=(self.child_conn, self.input_queue, self.output_queue), daemon=True)

    def terminate(self) -> None:
        self.parent_conn.close()
        return super().terminate()


def do_process_file(conn, input_queue : ProcessQueue, output_queue: ProcessQueue):
    set_cuda_environment('12.3')
    model : WhisperModel = WhisperModel('medium', device='cuda')
    conn.send('init_finished')

    num_producers = 3
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


def set_cuda_environment(cuda_version):
    cuda_path = f"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v{cuda_version}"
    bin_path = os.path.join(cuda_path, 'bin')
    libnvvp_path = os.path.join(cuda_path, 'libnvvp')

    # Set CUDA_HOME
    os.environ['CUDA_PATH'] = cuda_path

    # Add CUDA bin and libnvvp to PATH
    current_path = os.environ.get('Path', '')
    new_path = f"{bin_path};{libnvvp_path};{current_path};C:\\Program Files (x86)\\NVIDIA Corporation\\PhysX\\Common;C:\\Program Files\\NVIDIA Corporation\\Nsight Compute 2023.2.2\\;C:\\Program Files\\NVIDIA Corporation\\NVIDIA NvDLISR"
    os.environ['Path'] = new_path

    print("CUDA environment variables set for this session.")

    print('There are %d GPU(s) available.' % cuda.device_count())
    if cuda.is_available():
        print('We will use the GPU:', cuda.get_device_name(0))
    else:
        print('No GPU available, using the CPU instead.')
            
        

    

    