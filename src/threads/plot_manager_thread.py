from customtkinter import BOTH, TOP, CTkToplevel
from models.settings import Settings
from models.audio_file import AudioFile
from threads.speech_base_thread import SpeechBaseThread
from models.audio_file import AudioFile
from managers.audio_file_manager import AudioFileManager


class PlotManagerThread(SpeechBaseThread):
    def __init__(self, master: CTkToplevel, audio_manager: AudioFileManager,  audio_file: AudioFile):
        super().__init__('PlotManagerThread', Settings(), self.on_error)
        self.master = master
        self.audio_manager = audio_manager
        self.audio_file = audio_file

    def do_run(self):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        import numpy as np

        self.audio_file = self.audio_manager.get_by_path(
            self.audio_file.file_path)
        if self.audio_file is None or self.audio_file.length > 60 * 1000:
            return

        from custom_pydub.custom_audio_segment import AudioSegment
        audio: AudioSegment = AudioSegment.from_wav(self.audio_file.file_path)

        if audio.channels == 1:
            samples_float = np.array(
                audio.get_array_of_samples()).astype(np.float32)
        else:
            # Stereo
            left_channel = audio.split_to_mono()[0]
            right_channel = audio.split_to_mono()[1]

            # You can either process them separately or mix them down to mono
            # Here's how you might mix them to mono
            samples_left = np.array(
                left_channel.get_array_of_samples()).astype(np.float32)
            samples_right = np.array(
                right_channel.get_array_of_samples()).astype(np.float32)
            samples_float = np.minimum(samples_left, samples_right)

        normalized_samples = samples_float / \
            (2**(audio.sample_width * 8 - 1) - 1)
        normalized_samples[normalized_samples == 0] = np.finfo(float).eps
        samples_dBFS = 20 * np.log10(np.abs(normalized_samples))
        clipped_samples_dBFS = np.clip(samples_dBFS, -50, 0)
        times = np.arange(len(clipped_samples_dBFS)) / float(audio.frame_rate)

        # Create a Matplotlib figure and axes
        fig = Figure(figsize=(15, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(times, clipped_samples_dBFS)
        ax.set_title('Audio Amplitúdó idő szerint (dBFS)')
        ax.set_ylabel('Amplitúdó (dBFS)')
        ax.set_xlabel('Idő (másodperc)')
        ax.set_xticks(np.arange(0, times[-1], 2))
        ax.set_xlim([0, times[-1]])
        ax.grid(True)

        # Embed the figure in the Tkinter window
        # A tk.DrawingArea.
        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1, pady=(15, 15))
        canvas.draw()

    def on_error(self, e, name):
        pass
