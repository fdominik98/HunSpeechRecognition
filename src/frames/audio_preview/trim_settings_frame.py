from customtkinter import CTkFrame, CTkLabel, CTkSlider, IntVar, CTkCheckBox
from utils.fonts import label_font
from models.settings import Settings


class TrimSettingsFrame(CTkFrame):
    def __init__(self, parent, row, column, settings: Settings):
        super().__init__(parent)

        self.grid(row=row, column=column, sticky='nsew')

        self.settings: Settings = settings

        self.noise_dbfs_label = CTkLabel(
            self, text="Csend limit:", height=10, font=label_font())
        self.noise_dbfs_label.grid(
            row=0, column=0, padx=15, pady=(10, 0), sticky='nsw')

        self.dbfs_auto_var = IntVar(value=int(self.settings.trim_dbfs_auto))
        self.dbfs_auto_checkbox = CTkCheckBox(self, checkbox_width=18, checkbox_height=18,
                                              text="Auto", variable=self.dbfs_auto_var, command=self.__on_dbfs_auto_change)
        self.dbfs_auto_checkbox.grid(
            row=0, column=0, padx=0, pady=(10, 0), sticky='nse')

        # Create a Scale widget
        self.noise_dbfs_slider = CTkSlider(
            self, from_=-50, to=-10, command=self.__on_noise_db_slider_change)
        self.noise_dbfs_slider.set(self.settings.noise_threshold)
        self.noise_dbfs_slider.grid(
            row=1, column=0, padx=15, pady=0, sticky='nsew')

        self.noise_dbfs_value_label = CTkLabel(self,
                                               text=f'{self.noise_dbfs_slider.get():.1f} dBFS',
                                                        height=10, font=label_font())
        self.noise_dbfs_value_label.grid(
            row=2, column=0, padx=15, pady=0, sticky='nsew')

        self.noise_dur_label = CTkLabel(
            self, text="Csend időtartama:", height=10, font=label_font())
        self.noise_dur_label.grid(
            row=3, column=0, padx=15, pady=(10, 0), sticky='nsw')
        # Create a Scale widget
        self.noise_dur_slider = CTkSlider(
            self, from_=0.5, to=5, command=self.__on_noise_dur_slider_change)
        self.noise_dur_slider.set(self.settings.silence_dur)
        self.noise_dur_slider.grid(
            row=4, column=0, padx=15, pady=0, sticky='nsew')

        self.noise_dur_value_label = CTkLabel(self,
                                              text=f'{self.noise_dur_slider.get():.2f} másodperc',
                                              height=10,
                                              font=label_font())
        self.noise_dur_value_label.grid(
            row=5, column=0, padx=15, pady=(0, 10), sticky='nsew')

        self.__on_dbfs_auto_change()

    def __on_noise_db_slider_change(self, value):
        self.noise_dbfs_value_label.configure(text=f'{value:.1f} dBFS')
        self.settings.noise_threshold = value

    def __on_noise_dur_slider_change(self, value):
        self.noise_dur_value_label.configure(text=f'{value:.2f} másodperc')
        self.settings.silence_dur = int(round(value * 1000))

    def __on_dbfs_auto_change(self):
        value = bool(self.dbfs_auto_checkbox.get())
        self.settings.trim_dbfs_auto = bool(value)
        if value:
            self.noise_dbfs_slider.grid_remove()
            self.noise_dbfs_value_label.grid_remove()
        else:
            self.noise_dbfs_slider.grid()
            self.noise_dbfs_value_label.grid()

    def set_frame_state(self, state):
        for child in self.winfo_children():
            child.configure(state=state)
