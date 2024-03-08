import os
from typing import Optional
from multiprocessing import freeze_support
from customtkinter import CTk, filedialog, CTkFrame, CTkTextbox, CTkLabel, CTkButton, CTkProgressBar, set_appearance_mode, set_default_color_theme, DISABLED, NORMAL
from managers.settings_manager import SettingsManager
from utils.general_utils import empty, get_text
from utils.window_utils import open_message, center_window
from utils.fonts import button_font, label_font
from windows.main_window import MainWindow
from models.pipeline_process import PipelineProcess, ModelInitState
from managers.environment_manager import EnvironmentManager
from models.environment import get_images_path
from custom_logging.setup_logging import setup_logging
from utils.audio_converter import audio_file_formats
from threads.project_loader_thread import ProjectLoaderThread, ProjectCreatorThread


freeze_support() # Preventing multiple windows in production

set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

TITLE = "Transzkriptor Prototípus"
ICON = f'{get_images_path()}/icon.ico'

setup_logging()

class ProjectInterface(CTk):   
    
    def __init__(self):
        super().__init__()

        self.pipeline_process = PipelineProcess()
        self.pipeline_process.start()

        self.message_window = None
        self.project_loader_thread : Optional[ProjectLoaderThread] = None
        self.main_app_window : Optional[MainWindow] = None
        self.loading_state = False

        # configure window
        center_window(self, 500, 500)
        self.title(TITLE)
        self.iconbitmap(default=ICON)        

        try:
            self.environment_manager = EnvironmentManager()
        except Exception as e:
            open_message(self, 'hiba', e)
            self.message_window.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.side_bar = CTkFrame(self, corner_radius=0)
        self.side_bar.grid(row=0, column=0, padx=(5,0), sticky="nsew")
        self.side_bar.grid_columnconfigure(0, weight=1)  

        self.project_folder_label = CTkLabel(self.side_bar, text="Projekt mappa:", height=10, font=label_font())
        self.project_folder_label.grid(row=0, column=0, padx=20, pady=(40,0), sticky='sw')
        self.project_folder_textbox = CTkTextbox(self.side_bar, height=30)
        self.project_folder_textbox.grid(row=1, column=0, padx=20, pady=(10,0), sticky='nsew')
        self.__bind_textbox_click(self.project_folder_textbox, self.__browse_project_folder)


        self.project_name_label = CTkLabel(self.side_bar, text="Project neve:", height=10, font=label_font())
        self.project_name_label.grid(row=2, column=0, padx=20, pady=(40,0), sticky='nsew')
        self.project_name_textbox = CTkTextbox(self.side_bar, height=30, wrap='word')
        self.project_name_textbox.grid(row=3, column=0, padx=40, pady=(10,0), sticky='nsew')
        self.project_name_textbox.bind("<Key>", lambda e: self.__center_pname_textbox())


        self.input_file_label = CTkLabel(self.side_bar, text="Hangfájl:", height=10, font=label_font())
        self.input_file_label.grid(row=4, column=0, padx=20, pady=(40,0), sticky='sw')
        self.input_file_textbox = CTkTextbox(self.side_bar, height=30, wrap='word')
        self.input_file_textbox.grid(row=5, column=0, padx=20, pady=(10,0), sticky='nsew')
        self.input_file_textbox.configure(state=DISABLED)
       
        self.__bind_textbox_click(self.input_file_textbox, self.__browse_input_file)        


        self.load_project_button = CTkButton(self.side_bar, command=self.__load_project, text="Project betöltése", font=button_font())
        self.load_project_button.grid(row=6, column=0, padx=20, pady=(40,0), sticky='nsew')

        self.create_project_button = CTkButton(self.side_bar, command=self.__create_project, text="Projekt létrehozása", font=button_font())
        self.create_project_button.grid(row=7, column=0, padx=20, pady=10, sticky='nsew')

        self.loading_progressbar = CTkProgressBar(self, orientation="horizontal", height=10, corner_radius=0, determinate_speed=2.5)
        self.loading_progressbar.grid(row=8, column=0, padx=20, pady=(10, 5), sticky="wsne") 
        self.loading_progressbar.grid_remove()  

        self.loading_label = CTkLabel(self, text="", height=10, bg_color='transparent', fg_color='transparent')
        self.loading_label.grid(row=9, column=0, padx=20, pady=(0, 10), sticky='wsne')
        self.loading_label.grid_remove()

        self.grid_columnconfigure(0, weight=1, minsize=400)
        self.grid_rowconfigure(0, weight=1)

        self.init_project_folder(self.environment_manager.get_last_project_dir())            

        self.__set_loading_state('')
        self.__handle_process_on_startup()


    def __center_pname_textbox(self):
        self.project_name_textbox.tag_config("center", justify='center')
        self.project_name_textbox.tag_add("center", 1.0, "end")


    def __browse_input_file(self, e):
        if self.loading_state:
            return
        file_path = filedialog.askopenfilename(filetypes=audio_file_formats)
        self.__set_input_file(file_path)

       
    def __browse_project_folder(self, e):
        if self.loading_state:
            return
        directory = filedialog.askdirectory()
        self.init_project_folder(directory)


    def init_project_folder(self, directory):
        if self.__is_project(directory):
            settings_manager = SettingsManager(directory)
            self.__set_project_name(settings_manager.get().project_name)
            self.__set_input_file(settings_manager.get().project_audio_path)
            self.project_name_textbox.configure(state=DISABLED)
            self.create_project_button.configure(state=DISABLED)
            self.load_project_button.configure(state=NORMAL)
        else:
            self.create_project_button.configure(state=NORMAL)
            self.load_project_button.configure(state=DISABLED)
            self.__set_project_name('')
            self.__set_input_file('')

        self.__set_project_folder(directory)


    def __set_input_file(self, path : str):
        self.input_file_textbox.configure(state=NORMAL)
        self.input_file_textbox.delete("0.0", "end")
        self.input_file_textbox.insert("0.0", path)
        self.input_file_textbox.configure(state=DISABLED)

    def __set_project_folder(self, path : str):
        self.project_folder_textbox.configure(state=NORMAL)
        self.project_folder_textbox.delete("0.0", 'end')
        self.project_folder_textbox.insert("0.0", path) 
        self.project_folder_textbox.configure(state=DISABLED)

    def __set_project_name(self, name: str):
        self.project_name_textbox.configure(state=NORMAL)
        self.project_name_textbox.delete("0.0", 'end')
        self.project_name_textbox.insert("0.0", name) 
        self.__center_pname_textbox()

    def __bind_textbox_click(self, textbox : CTkTextbox, callback):
        textbox.bind("<Button-1>", command=callback)
        textbox.bind("<Enter>", lambda e, textbox=textbox: self.__highlight_textbox(textbox))
        textbox.bind("<Leave>", lambda e, textbox=textbox: self.__unhighlight_textbox(textbox))
    
    def __highlight_textbox(self, textbox : CTkTextbox):
        textbox.configure(cursor="hand2")

    def __unhighlight_textbox(self, textbox : CTkTextbox):
        textbox.configure(cursor="arrow")

    def __is_project(self, path : str):
        return os.path.exists(f'{path}/.audiorecproj')

    def __create_project(self):
        project_name = get_text(self.project_name_textbox)
        project_base_folder = get_text(self.project_folder_textbox)
        input_file = get_text(self.input_file_textbox)

        if empty(project_name):
            open_message(self, 'hiba', 'Add meg a projekt nevét!')
            return
        if empty(input_file):
            open_message(self, 'hiba', 'Tölts be egy hangfájlt!')
            return
        
        project_dir = f'{project_base_folder}/{project_name}'
        if os.path.exists(project_dir):
            open_message(self, 'hiba', 'A projekt már létezik ebben a mappában.')
            return
        
        if self.__is_project(project_base_folder):
            open_message(self, 'hiba', 'A projekt nem hozható létre egy másik projekt mappában.')
            return
        
        os.makedirs(project_dir)        
        self.project_loader_thread = ProjectCreatorThread(self.load_error_callback, self.environment_manager, project_dir, input_file, project_name) 
        self.__set_loading_state('Projekt létrehozása')
        self.project_loader_thread.start()
        self.__open_main_application()


    def __load_project(self):
        directory = get_text(self.project_folder_textbox)
        if not os.path.exists(f'{directory}/.audiorecproj'):
            open_message(self, 'hiba', 'A projekt nem található.')
            return
        self.project_loader_thread = ProjectLoaderThread(self.load_error_callback, self.environment_manager, directory)
        self.__set_loading_state('Projekt betöltése')
        self.project_loader_thread.start()
        self.__open_main_application()


    def load_error_callback(self, message, thread):
        open_message(self, "hiba", f'{message} - {thread}') 
        self.__unset_loading_state()


    def __open_main_application(self):
        if self.project_loader_thread is None:
            return
        if self.project_loader_thread.is_alive():
            self.after(300, self.__open_main_application)
            return
        self.main_app_window = MainWindow(self.master, self.project_loader_thread.settings, self.pipeline_process)
        self.__unset_loading_state()
        self.withdraw()
        self.main_app_window.protocol("WM_DELETE_WINDOW", lambda settings_manager=self.project_loader_thread.settings_manager: self.on_main_window_closing(settings_manager))
        self.main_app_window.iconbitmap(ICON)
        self.main_app_window.title(TITLE)
        center_window(self.main_app_window, 1100, 720)
        self.main_app_window.state('zoomed')


    def on_main_window_closing(self, settings_manager : SettingsManager):
        if self.main_app_window is None:
            return
        settings_manager.save_settings()
        self.main_app_window.withdraw()
        self.deiconify()
        self.__unset_loading_state()
        self.main_app_window.destroy_threads()
        self.main_app_window.destroy()

    def __unset_loading_state(self):
        self.loading_state = False
        self.loading_progressbar.grid_remove()  
        self.loading_label.grid_remove()
        self.loading_progressbar.stop()
        self.init_project_folder(get_text(self.project_folder_textbox))

    def __set_loading_state(self, label_text : str):
        self.loading_label.configure(text=label_text)
        if not self.loading_state:
            self.loading_state = True
            self.loading_progressbar.grid()
            self.loading_progressbar.start()
            self.loading_label.grid()  
            self.load_project_button.configure(state=DISABLED)
            self.create_project_button.configure(state=DISABLED)
            self.project_name_textbox.configure(state=DISABLED)


    def __handle_process_on_startup(self):        
        if self.pipeline_process.download_parent_conn.poll():
            state : ModelInitState = self.pipeline_process.download_parent_conn.recv()
            if state is ModelInitState.CHECKING_FOR_MODEL:
                self.__set_loading_state('Model keresése')
            elif state is ModelInitState.CHECKING_FOR_CONN:
                self.__set_loading_state('Hálózati kapcsolat ellenőrzés')
            elif state is ModelInitState.DOWNLOADING_MODEL:
                self.__set_loading_state('Model letöltése. Ne szakítsd meg az internet kapcsolatot!')
            elif state is ModelInitState.MODEL_FOUND:
                self.__unset_loading_state()
                return
            elif state is ModelInitState.NO_CONN:
                self.__set_loading_state('Nincs hálózati kapcsolat. Csatlakozz az internethez!')
            elif state is ModelInitState.ERROR:
                pass
        self.after(300, self.__handle_process_on_startup)
            
def main():
    app = ProjectInterface()
    app.mainloop()
    
if __name__ == "__main__":
    main()

