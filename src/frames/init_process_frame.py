from customtkinter import CTkFrame, CTkProgressBar


class InitProcessFrame(CTkFrame):
    def __init__(self, parent, row, column):
        super().__init__(parent, height=10)

        self.grid(row=row, column=column, rowspan=1, pady=(0, 10), sticky="nsew")

        self.init_progressbar = CTkProgressBar(self, orientation="horizontal", height=5, corner_radius=0, determinate_speed=2.5)
        self.init_progressbar.grid(row=0, column=0, padx=0, pady=0, sticky="wsne") 

        self.grid_columnconfigure(0, weight=1)   

    def pipeline_init_start_callback(self):
        self.init_progressbar.grid()  
        self.init_progressbar.start()

    def init_finish_callback(self):
        print('pipeline init finished.')
        self.init_progressbar.stop()
        self.init_progressbar.grid_remove()