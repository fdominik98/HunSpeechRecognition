from PIL import Image
from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage
from utils.fonts import label_font
from widgets.interactive_textbox import ResultInteractiveTextbox
from managers.result_manager import ResultManager
from managers.audio_file_manager import TrimmedAudioFileManager, SplitAudioFileManager
from models.result_row import ResultRow
from models.environment import get_images_path
from models.process_state import ProcessState
from models.settings import Settings

class ResultPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, settings: Settings, result_manager : ResultManager, split_audio_file_manager : SplitAudioFileManager, trimmed_audio_file_manager: TrimmedAudioFileManager, audio_load_callback, audio_play_callback):
        super().__init__(parent)
        self.settings = settings
        self.result_manager : ResultManager = result_manager

        self.delete_all_icon = CTkImage(Image.open(f'{get_images_path()}/delete_all.png'), size=(17, 17))
        
        self.grid(row=row, column=column, pady=20, sticky="swne")

        # create textbox
        self.result_preview_label = CTkLabel(self, text="Előnézet:", height=10, font=label_font())
        self.result_preview_label.grid(row=0, pady=(10, 10), padx=10, sticky="ws")

        self.delete_button = CTkButton(self, fg_color="transparent", border_width=2, width=50, height=5, text_color=("gray10", "#DCE4EE")
                                                     ,command=self.__delete_all_results, text="", image=self.delete_all_icon)
        self.delete_button.grid(row=0, padx=15, pady=(10,0), sticky="se")

        self.textbox = ResultInteractiveTextbox(result_manager=result_manager,
                                                master=self,
                                                trimmed_audio_file_manager=trimmed_audio_file_manager,
                                                split_audio_file_manager=split_audio_file_manager,
                                                audio_load_callback=audio_load_callback,
                                                audio_play_callback=audio_play_callback,
                                                selection_changed_callback=self.selection_changed,
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
            self.textbox.clear()

    def on_process_state_change(self, old_process_state : ProcessState, process_state : ProcessState, trim_enabled : bool, forced : bool):
        if process_state is ProcessState.STOPPED:
            self.delete_button.configure(state="normal")
        else:
            self.delete_button.configure(state="disabled")

    def selection_changed(self):
        pass

        
    def update_textbox(self):
        if not self.winfo_exists():
            return
        found = False
        if not self.result_manager.insert_widget_queue.empty():
            result : ResultRow = self.result_manager.insert_widget_queue.get()
            self.textbox.insert(result.id, result.sentence)
            found = True
        if found:
            self.after(0, self.update_textbox)
        else:
            self.after(1000, self.update_textbox)
