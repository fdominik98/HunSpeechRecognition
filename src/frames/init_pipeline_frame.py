from queue import Queue
from customtkinter import CTkFrame, CTkProgressBar
from models.pipeline_process import ModelInitState


class InitPipelineFrame(CTkFrame):
    def __init__(self, parent, row, column, init_pipeline_queue: Queue):
        super().__init__(parent, height=10)
        self.init_pipeline_queue: Queue = init_pipeline_queue

        self.grid(row=row, column=column, rowspan=1,
                  pady=(0, 10), sticky="nsew")

        self.init_progressbar = CTkProgressBar(
            self, orientation="horizontal", height=5, corner_radius=0, determinate_speed=2.5)
        self.init_progressbar.grid(
            row=0, column=0, padx=0, pady=0, sticky="wsne")

        self.grid_columnconfigure(0, weight=1)

        self.update_frame()

    def pipeline_init_start_callback(self):
        self.init_progressbar.grid()
        self.init_progressbar.start()

    def init_finish_callback(self):
        print('pipeline init finished.')
        self.init_progressbar.stop()
        self.init_progressbar.grid_remove()

    def update_frame(self):
        if not self.winfo_exists():
            return

        if not self.init_pipeline_queue.empty():
            init_state = self.init_pipeline_queue.get()
            if init_state is ModelInitState.INIT_STARTED:
                self.pipeline_init_start_callback()
            elif init_state is ModelInitState.INIT_FINISHED:
                self.init_finish_callback()

        self.after(500, self.update_frame)
