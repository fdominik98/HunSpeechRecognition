from customtkinter import CTkToplevel
from models.environment import get_images_path

class ToplevelWindow(CTkToplevel):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.after(250, lambda: self.iconbitmap(f'{get_images_path()}/icon.ico'))