import subprocess
def run_ffmpeg_command(command, input = None, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    process = subprocess.Popen(command, stdin=stdin, stdout=stdout, stderr=stderr, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
    output, error = process.communicate(input=input)
    return process, output, error
