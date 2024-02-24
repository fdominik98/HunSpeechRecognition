from PIL import Image
from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage
from utils.fonts import label_font
from widgets.interactive_textbox import ResultInteractiveTextbox
from managers.result_manager import ResultManager
from managers.audio_file_manager import TrimmedAudioFileManager
from models.result_row import ResultRow
from models.environment import get_images_path
from models.process_state import ProcessState

class ResultPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, result_manager : ResultManager, trimmed_audio_manager: TrimmedAudioFileManager, audio_load_callback, audio_play_callback):
        super().__init__(parent)

        self.result_manager : ResultManager = result_manager
        self.trimmed_audio_manager : TrimmedAudioFileManager = trimmed_audio_manager

        self.trash_icon = CTkImage(Image.open(f'{get_images_path()}/trash.png'), size=(17, 17))
        
        self.grid(row=row, column=column, pady=20, sticky="swne")

        # create textbox
        self.result_preview_label = CTkLabel(self, text="Előnézet:", height=10, font=label_font())
        self.result_preview_label.grid(row=0, pady=(10, 10), padx=10, sticky="ws")

        self.delete_button = CTkButton(self, fg_color="transparent", border_width=2, width=50, height=5, text_color=("gray10", "#DCE4EE")
                                                     ,command=self.__delete_all_results, text="", image=self.trash_icon)
        self.delete_button.grid(row=0, padx=15, pady=(10,0), sticky="se")

        self.textbox = ResultInteractiveTextbox(result_manager=result_manager,
                                                trimmed_audio_manager=trimmed_audio_manager,
                                                master=self,
                                                audio_load_callback=audio_load_callback,
                                                audio_play_callback=audio_play_callback,
                                                height=350)
        self.textbox.grid(row=1, pady=(5, 5), padx=10, sticky="wsne")        

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=10)
        self.grid_rowconfigure(1, weight=1, minsize=300)

        self.update_textbox()
        

    def __delete_all_results(self):
        response = messagebox.askyesno("Törlés", "Biztos törlöd a összes feldolgozott szöveget?")
        if response:
            self.result_manager.delete_all()
            self.textbox.clear_rows()

    def on_process_state_change(self, process_state : ProcessState, forced : bool):
        if process_state is ProcessState.STOPPED:
            self.delete_button.configure(state="normal")
        else:
            self.delete_button.configure(state="disabled")

        
    def update_textbox(self):
        if not self.winfo_exists():
            return
        found = False
        if not self.result_manager.insert_widget_queue.empty():
            result : ResultRow = self.result_manager.insert_widget_queue.get()
            self.textbox.insert_row(result.id + 1, result.sentence)
            found = True
        if found:
            self.after(0, self.update_textbox)
        else:
            self.after(1000, self.update_textbox)