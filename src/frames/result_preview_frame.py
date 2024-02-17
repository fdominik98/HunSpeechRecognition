from customtkinter import CTkFrame, CTkLabel
from utils.fonts import label_font
from tktooltip import ToolTip
from widgets.interactive_textbox import ResultInteractiveTextbox
from managers.result_manager import ResultManager
from models.result_row import ResultRow

class ResultPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, result_manager : ResultManager, audio_load_callback, audio_play_callback):
        super().__init__(parent)

        self.result_manager : ResultManager = result_manager
        
        self.grid(row=row, column=column, pady=20, sticky="swne")

        # create textbox
        self.result_preview_label = CTkLabel(self, text="Előnézet:", height=10, font=label_font())
        self.result_preview_label.grid(row=0, pady=(10, 10), padx=10, sticky="ws")

        self.textbox = ResultInteractiveTextbox(result_manager=result_manager, master=self,
                                            audio_load_callback=audio_load_callback,
                                            audio_play_callback=audio_play_callback,
                                            height=350)
        self.textbox.grid(row=1, pady=(5, 5), padx=10, sticky="wsne")        

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=10)
        self.grid_rowconfigure(1, weight=1, minsize=300)


        # self.tooltip = ToolTip(self.result_preview_textbox, msg=self.interactive_text_manager.get_timestamp,
        #                        delay=0.01, follow=True,
        #                        fg="white", bg="black", padx=2, pady=2, font=label_font())

        self.update_textbox()
        
        
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