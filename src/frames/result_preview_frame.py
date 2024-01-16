from customtkinter import CTkFrame, CTkLabel, CTkTextbox
from utils.fonts import textbox_font, label_font
from tktooltip import ToolTip
from managers.interactive_text_manager import InteractiveTextManager
from queue import Queue

class ResultPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, interactive_text_manager):
        super().__init__(parent)
        
        self.grid(row=row, column=column, pady=20, sticky="swne")

        # create textbox
        self.result_preview_label = CTkLabel(self, text="Előnézet:", height=10, font=label_font())
        self.result_preview_label.grid(row=0, pady=(10, 10), padx=10, sticky="ws")

        self.result_preview_textbox = CTkTextbox(self, font=textbox_font(), text_color='black', fg_color='#D3D3D3', wrap='word', height=350)
        self.result_preview_textbox.grid(row=1, pady=(5, 5), padx=10, sticky="wsne")
        self.result_preview_textbox.configure(state="disabled")
        
        self.interactive_text_manager : InteractiveTextManager = interactive_text_manager
        self.interactive_text_manager.textbox = self.result_preview_textbox

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=10)
        self.grid_rowconfigure(1, weight=1, minsize=300)


        self.tooltip = ToolTip(self.result_preview_textbox, msg=self.interactive_text_manager.get_timestamp,
                               delay=0.01, follow=True,
                               fg="white", bg="black", padx=2, pady=2, font=label_font())

        self.update_textbox()
        
        
    def update_textbox(self):
        found = False
        if not self.interactive_text_manager.result_manager.widget_queue.empty():
            self.interactive_text_manager.insert_text(self.interactive_text_manager.result_manager.widget_queue.get())
            found = True
        if found:
            self.after(1000, self.update_textbox)
        else:
            self.after(20, self.update_textbox)