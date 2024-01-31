from customtkinter import CTkFrame, CTkLabel, CTkTextbox, NONE
from utils.fonts import textbox_font, label_font
from tktooltip import ToolTip
from managers.interactive_text_manager import InteractiveTextManager

class ResultPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, result_manager, audio_load_callback, audio_play_callback):
        super().__init__(parent)
        
        self.grid(row=row, column=column, pady=20, sticky="swne")

        # create textbox
        self.result_preview_label = CTkLabel(self, text="Előnézet:", height=10, font=label_font())
        self.result_preview_label.grid(row=0, pady=(10, 10), padx=10, sticky="ws")

        self.result_preview_textbox = CTkTextbox(self, font=textbox_font(), text_color='black', fg_color='#D3D3D3', wrap=NONE, height=350)
        self.result_preview_textbox.grid(row=1, pady=(5, 5), padx=10, sticky="wsne")
        self.result_preview_textbox.configure(state="disabled")

        self.interactive_text_manager = InteractiveTextManager(result_manager=result_manager,
                                                                textbox=self.result_preview_textbox,
                                                                audio_load_callback=audio_load_callback,
                                                                audio_play_callback=audio_play_callback)

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
        if not self.interactive_text_manager.result_manager.widget_queue.empty():
            self.interactive_text_manager.insert_text(self.interactive_text_manager.result_manager.widget_queue.get())
            found = True
        if found:
            self.after(0, self.update_textbox)
        else:
            self.after(1000, self.update_textbox)