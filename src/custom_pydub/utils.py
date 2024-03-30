import subprocess
import atexit

# Keep track of subprocesses to ensure they can be cleaned up on exit
_open_subprocesses = []

def patch_popen():
    def cleanup_subprocesses():
        for process in list(_open_subprocesses):  # Use a copy of the list for safe removal during iteration
            if process.poll() is not None:  # Check if process has already terminated
                _open_subprocesses.remove(process)
            else:
                try:
                    process.terminate()
                    process.wait(timeout=1)
                    _open_subprocesses.remove(process)
                except Exception as e:
                    print(f"Error terminating process: {e}")

    # Register the cleanup function to be called on exit
    atexit.register(cleanup_subprocesses)

    class CustomPopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            # Configure startup info for Windows to hide the window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Ensure no window is created
            kwargs['creationflags'] = kwargs.get('creationflags', 0) | subprocess.CREATE_NO_WINDOW
            
            # Set up the pipes as defaults
            kwargs.setdefault('stdin', subprocess.PIPE)
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.PIPE)
            kwargs['startupinfo'] = startupinfo

            super().__init__(*args, **kwargs)
            _open_subprocesses.append(self)
            
        def communicate(self, *args, **kwargs):
            output, error = super().communicate(*args, **kwargs)
            self.cleanup()  # Call cleanup method after process terminates
            return output, error

        def cleanup(self):
            """Remove the process from the tracking list if it has terminated."""
            if self.poll() is not None:  # Check if the process has terminated
                try:
                    _open_subprocesses.remove(self)
                except ValueError:
                    pass  # Process already removed, ignore

    # Patch the Popen class in the subprocess module
    subprocess.Popen = CustomPopen

def run_ffmpeg_command(command, input=None, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    process = subprocess.Popen(command, stdin=stdin, stdout=stdout, stderr=stderr,
                               startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
    output, error = process.communicate(input=input)
    return process, output, error
