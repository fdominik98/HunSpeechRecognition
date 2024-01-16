from customtkinter import CTk, filedialog, CTkFrame, CTkTextbox, CTkLabel, CTkButton, set_appearance_mode, set_default_color_theme
import os
from managers.settings_manager import SettingsManager
from utils.general_utils import empty, get_text
from utils.command_utils import get_audio_duration
from utils.window_utils import open_message, center_window
from utils.fonts import button_font, label_font
from windows.main_window import MainWindow
from shutil import copy
from managers.audio_file_manager import AudioFileManager
from models.audio_file import AudioFile

set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class ProjectInterface(CTk):   
    
    def __init__(self):
        super().__init__()
        self.message_window = None
        self.main_app_window = None

        # configure window
        self.title("Beszéd Felismerés Prototípus")
        self.geometry("500x720")
        center_window(self)
        
        self.side_bar = CTkFrame(self, corner_radius=0)
        self.side_bar.grid(row=0, column=0, padx=(5,0), sticky="nsew")
        self.side_bar.grid_columnconfigure(0, weight=1)  

        self.project_name_label = CTkLabel(self.side_bar, text="Project neve:", height=10, font=label_font())
        self.project_name_label.grid(row=0, column=0, padx=20, pady=(40,0), sticky='nsew')
        self.project_name_textbox = CTkTextbox(self.side_bar, height=30, wrap='word')
        self.project_name_textbox.grid(row=1, column=0, padx=40, pady=(10,0), sticky='nsew')
        self.project_name_textbox.insert("0.0", '')
        self.__center_pname_textbox()
        self.project_name_textbox.bind("<Key>", lambda e: self.__center_pname_textbox())


        self.input_file_label = CTkLabel(self.side_bar, text="Hangfájl:", height=10, font=label_font())
        self.input_file_label.grid(row=2, column=0, padx=20, pady=(40,0), sticky='sw')
        self.input_file_textbox = CTkTextbox(self.side_bar, height=30, wrap='word')
        self.input_file_textbox.grid(row=3, column=0, padx=20, pady=(10,0), sticky='nsew')
        self.input_file_textbox.insert("0.0", '')
        self.input_file_textbox.configure(state="disabled")
       
        self.__bind_textbox_click(self.input_file_textbox, self.__browse_input_file)
        
        self.project_folder_label = CTkLabel(self.side_bar, text="Projekt mappa:", height=10, font=label_font())
        self.project_folder_label.grid(row=4, column=0, padx=20, pady=(40,0), sticky='sw')
        self.project_folder_textbox = CTkTextbox(self.side_bar, height=30)
        self.project_folder_textbox.grid(row=5, column=0, padx=20, pady=(10,0), sticky='nsew')
        self.project_folder_textbox.insert("0.0", 'C:/Users/freyd/Desktop/anya/PROBA')
        self.project_folder_textbox.configure(state="disabled")

        self.__bind_textbox_click(self.project_folder_textbox, self.__browse_project_folder)


        self.load_project_button = CTkButton(self.side_bar, command=self.__load_project, text="Project betöltése", font=button_font())
        self.load_project_button.grid(row=6, column=0, padx=20, pady=(40,0), sticky='nsew')

        self.create_project_button = CTkButton(self.side_bar, command=self.__create_project, text="Projekt létrehozása", font=button_font())
        self.create_project_button.grid(row=7, column=0, padx=20, pady=10, sticky='nsew')

        self.grid_columnconfigure(0, weight=1, minsize=400)
        self.grid_rowconfigure(0, weight=1)


    def __center_pname_textbox(self):
        self.project_name_textbox.tag_config("center", justify='center')
        self.project_name_textbox.tag_add("center", 1.0, "end")


    def __browse_input_file(self, e):
        filename = filedialog.askopenfilename(filetypes=(("MP3 files", "*.mp3"),))
        self.input_file_textbox.configure(state="normal")
        self.input_file_textbox.delete("0.0", "end")
        self.input_file_textbox.insert("0.0", filename)
        self.input_file_textbox.configure(state="disabled")

       
    def __browse_project_folder(self, e):
        directory = filedialog.askdirectory()
        self.project_folder_textbox.configure(state="normal")
        self.project_folder_textbox.delete("0.0", 'end')
        self.project_folder_textbox.insert("0.0", directory) 
        self.project_folder_textbox.configure(state="disabled")

    def __bind_textbox_click(self, textbox : CTkTextbox, callback):
        textbox.bind("<Button-1>", command=callback)
        textbox.bind("<Enter>", lambda e, textbox=textbox: self.__highlight_textbox(textbox))
        textbox.bind("<Leave>", lambda e, textbox=textbox: self.__unhighlight_textbox(textbox))
    
    def __highlight_textbox(self, textbox : CTkTextbox):
        textbox.configure(cursor="hand2")

    def __unhighlight_textbox(self, textbox : CTkTextbox):
        textbox.configure(cursor="arrow")


    def __create_project(self):
        project_name = get_text(self.project_name_textbox)
        if empty(project_name):
            open_message(self, 'hiba', 'Add meg a projekt nevét!')
            return
        input_file = get_text(self.input_file_textbox)
        if empty(input_file):
            open_message(self, 'hiba', 'Tölts be egy hangfájlt!')
            return
        
        directory = f'{get_text(self.project_folder_textbox)}/{project_name}'
        if os.path.exists(directory):
            open_message(self, 'hiba', 'A projekt már létezik ebben a mappában.')
            return
        
        os.makedirs(directory)

        audio_manager = AudioFileManager(directory)
        mp3_file = f'{directory}/audio.mp3'
        copy(input_file, mp3_file)
        mp3_duration = get_audio_duration(mp3_file) 
        audio_manager.save_audio_file(AudioFile(0, mp3_file, (0, mp3_duration), (0, mp3_duration)))


        with open(f'{directory}/.audiorecproj', 'w') as file:
            file.write('')

        settings_manager = SettingsManager(directory)
        settings_manager.get().project_folder = directory
        settings_manager.get().mp3_file = mp3_file
        settings_manager.get().mp3_duration = mp3_duration
        settings_manager.save_settings()

        self.__open_main_application(settings_manager)



    def __load_project(self):
        directory = get_text(self.project_folder_textbox)
        if not os.path.exists(f'{directory}/.audiorecproj'):
            open_message(self, 'hiba', 'A projekt nem található.')
            return
        settings_manager = SettingsManager(directory)

        self.__open_main_application(settings_manager)


    def __open_main_application(self, settings_manager : SettingsManager):
        self.withdraw()
        self.main_app_window = MainWindow(settings_manager.get())        
        # When the main application is closed, end the program
        self.main_app_window.protocol("WM_DELETE_WINDOW", lambda settings_manager=settings_manager: self.on_closing(settings_manager))


    def on_closing(self, settings_manager : SettingsManager):
        settings_manager.save_settings()
        self.main_app_window.destroy_threads()
        self.main_app_window.destroy()
        self.deiconify()


if __name__ == "__main__":
    app = ProjectInterface()
    app.mainloop()