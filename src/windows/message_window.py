from customtkinter import CTkToplevel, CTkTextbox, CTkButton
from utils.fonts import label_font, button_font


class MessageWindow(CTkToplevel):
    """Initializes a top-level window showing status messages.
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.textbox = CTkTextbox(
            self, height=100, font=label_font(), wrap='word')
        self.textbox.pack(padx=20, pady=20, fill='x')
        self.textbox.insert('0.0', message)
        self.textbox.configure(state="disabled")
        self.button = CTkButton(
            self, command=self.destroy, text="Bezár", font=button_font())
        self.button.pack(padx=20, pady=10)
