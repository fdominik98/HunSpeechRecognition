import os


def check_gpu():
    from py3nvml.py3nvml import (nvmlInit,
                                 nvmlDeviceGetCount,
                                 nvmlDeviceGetHandleByIndex,
                                 nvmlDeviceGetMemoryInfo,
                                 nvmlShutdown, NVMLError)
    try:
        nvmlInit()
        device_count = nvmlDeviceGetCount()
        if device_count > 0:
            # Assuming we're interested in the first GPU
            handle = nvmlDeviceGetHandleByIndex(0)
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_gb = memory_info.total / \
                (1024 ** 3)  # Convert bytes to GiB
            nvmlShutdown()
            return True, gpu_memory_gb
        else:
            return False, 0
    except NVMLError as e:
        print(f"Failed to access GPU information: {e}")
        return False, 0


def select_whisper_model_type_gpu():
    import psutil
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

    print(f"Based on your system's resources, the recommended Whisper model to use is: {
          model}")
    return (model, has_gpu)


def select_whisper_model_type_cpu():
    import psutil
    # Check system properties
    cpu_cores = psutil.cpu_count(logical=False)
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GiB
    cpu_freq = psutil.cpu_freq().current / 1000.0

    print(f'CPU cores: {cpu_cores}')
    print(f'Total RAM (GB): {total_ram_gb}')
    print(f'CPU freq (GHz): {cpu_freq}')

    # Define thresholds for model selection
    ram_threshold_for_large = 16  # in GiB
    cpu_core_threshold_for_large = 8  # in GiB
    cpu_freq_threshold_for_large = 3

    if cpu_cores >= cpu_core_threshold_for_large and total_ram_gb >= ram_threshold_for_large and cpu_freq >= cpu_freq_threshold_for_large:
        model = 'large'
    else:
        model = 'medium'

    print(f"Based on your system's resources, the recommended Whisper model to use is: {
          model}")
    return model


def check_whisper_model(model_type, model_path) -> bool:
    if not os.path.exists(model_path):
        os.makedirs(model_path)
        return False
    return any(model_type in item for item in os.listdir(model_path))


def check_internet():
    from requests import get, ConnectionError
    try:
        response = get('http://www.google.com')
        return True
    except ConnectionError:
        return False
