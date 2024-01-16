from collections.abc import Mapping
from multiprocessing import Queue as ProcessQueue, Pipe, Process
from typing import Any
from multiprocessing import Queue as ProcessQueue
from torch import cuda
import os
from models.task import Task
from faster_whisper import WhisperModel
from models.result_row import ResultRow

class PipelineProcess(Process):
    def __init__(self) -> None:
        self.parent_conn, self.child_conn = Pipe()
        self.input_queue = ProcessQueue()
        self.output_queue = ProcessQueue()
        super().__init__(target=do_process_file, name="Pipeline process", args=(self.child_conn, self.input_queue, self.output_queue), daemon=True)

    def terminate(self) -> None:
        self.parent_conn.close()
        return super().terminate()

def do_process_file(conn, input_queue : ProcessQueue, output_queue: ProcessQueue):
    #pipe = init_pipeline()
    model : WhisperModel = init_pipeline2()
    conn.send('init_finished')

    while(True):
        task : Task = input_queue.get()
        result_list = run_pipeline2(model, task)
        output_queue.put(result_list)       


def run_pipeline2(model : WhisperModel, task : Task):
    segments, _ = model.transcribe(audio=task.trim_file_path, language='hu')
    result_list = []
    for segment in segments:
        result = ResultRow(task.segment_number, task.trim_file_path, (segment.start, segment.end),
                   (task.trim_timestamp[0] + segment.start, task.trim_timestamp[0] + segment.end), segment.text.strip())
        result_list.append(result)
    return result_list

def init_pipeline2():    
    set_cuda_environment('12.3')  # Replace with your CUDA version

    print('There are %d GPU(s) available.' % cuda.device_count())
    if cuda.is_available():
        print('We will use the GPU:', cuda.get_device_name(0))
        _device = 'cuda'        
    else:
        print('No GPU available, using the CPU instead.')
        _device = 'cpu'

    return WhisperModel('medium', device=_device, compute_type='float32')


# def run_pipeline(pipe, task : Task):
#     result = pipe(task.chunk_file_path, generate_kwargs={"language": "hungarian"}, return_timestamps=True)
#     result_dict_list = []
#     for chunk in result:
#         result_dict_list.append({'chunk_file' : task.chunk_file_path,
#                                 'relative_timestamp' : chunk['timestamp'],
#                                 'absolute_timestamp' : (task.chunk_timestamp[0] + chunk['timestamp'][0], task.chunk_timestamp[0] + chunk['timestamp'][1]),
#                                 'sentence' : chunk['text'].lstrip()})
#     return result_dict_list


# def init_pipeline():    
#     # Example usage
#     set_cuda_environment('12.3')  # Replace with your CUDA version

#     # If there's a GPU available...
#     print('There are %d GPU(s) available.' % cuda.device_count())
#     if cuda.is_available():
#         print('We will use the GPU:', cuda.get_device_name(0))
#         # Tell PyTorch to use the GPU.
#         _device = device('cuda:0')
#         torch_dtype = float16
#     else:
#         print('No GPU available, using the CPU instead.')
#         _device = device("cpu")
#         torch_dtype = float32

#     model_id = "openai/whisper-medium"

#     model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
#     model.to(_device)

#     processor = AutoProcessor.from_pretrained(model_id)

#     pipe = pipeline(
#         "automatic-speech-recognition",
#         model=model,
#         tokenizer=processor.tokenizer,
#         feature_extractor=processor.feature_extractor,
#         max_new_tokens=128,
#         chunk_length_s=30,
#         batch_size=16,
#         return_timestamps=True,
#         torch_dtype=torch_dtype,
#         device=device,
#     )
#     return pipe

def set_cuda_environment(cuda_version):
    cuda_path = f"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v{cuda_version}"
    bin_path = os.path.join(cuda_path, 'bin')
    libnvvp_path = os.path.join(cuda_path, 'libnvvp')

    # Set CUDA_HOME
    os.environ['CUDA_PATH'] = cuda_path

    # Add CUDA bin and libnvvp to PATH
    current_path = os.environ.get('PATH', '')
    new_path = f"{bin_path};{libnvvp_path};{current_path};C:\\Program Files (x86)\\NVIDIA Corporation\\PhysX\\Common;C:\\Program Files\\NVIDIA Corporation\\Nsight Compute 2023.2.2\\;C:\\Program Files\\NVIDIA Corporation\\NVIDIA NvDLISR"
    os.environ['PATH'] = new_path

    print("CUDA environment variables set for this session.")
            
        

    

    