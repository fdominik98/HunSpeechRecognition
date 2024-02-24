from customtkinter import CTkToplevel
from models.audio_file import AudioFile
from threads.plot_manager_thread import PlotManagerThread
from managers.audio_file_manager import AudioFileManager

class PlotWindow(CTkToplevel):
    """Initializes a top-level window showing status messages.
    """
    def __init__(self, audio_manager : AudioFileManager, audio_file : AudioFile, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        self.bind('<Button-1>', self.on_widget_click)
        self.plot_manager_thread = PlotManagerThread(master=self, audio_manager=audio_manager, audio_file=audio_file)
        self.plot_manager_thread.start()  

    def on_widget_click(self, event):
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)       
        

