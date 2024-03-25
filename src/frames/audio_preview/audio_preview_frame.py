from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage, CTkSwitch, BooleanVar, NORMAL, DISABLED
from utils.fonts import label_font
from models.environment import get_images_path
from models.settings import Settings
from managers.audio_file_manager import SplitAudioFileManager, TrimmedAudioFileManager, AudioFileManager
from models.process_state import ProcessState
from widgets.interactive_textbox import AudioInteractiveTextbox
from models.audio_file import AudioFile
from frames.audio_preview.trim_settings_frame import TrimSettingsFrame


class AudioPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, settings: Settings,
                 split_audio_manager: SplitAudioFileManager,
                 trimmed_audio_manager: TrimmedAudioFileManager,
                 original_audio_manager: AudioFileManager,
                 audio_load_callback, audio_play_callback, audio_stop_callback) -> None:
        super().__init__(parent)
        self.settings: Settings = settings
        self.split_audio_manager: SplitAudioFileManager = split_audio_manager
        self.trimmed_audio_manager: TrimmedAudioFileManager = trimmed_audio_manager
        self.original_audio_manager: AudioFileManager = original_audio_manager

        self.audio_stop_callback = audio_stop_callback
        self.trim_switch_flip_callbacks = []

        from PIL import Image
        self.delete_all_icon = CTkImage(Image.open(
            f'{get_images_path()}/delete_all.png'), size=(17, 17))
        self.trash_icon = CTkImage(Image.open(
            f'{get_images_path()}/trash.png'), size=(17, 17))

        self.grid(row=row, column=column, sticky='nsew')

        # Create a label
        self.trim_switch_label = CTkLabel(
            self, text="Trimmelés:", height=10, font=label_font())
        self.trim_switch_label.grid(
            row=0, column=0, padx=20, pady=(10, 5), sticky='nsw')

        # Create a switch
        self.trim_switch = CTkSwitch(self, text="", command=self.__on_trim_switch_flip, variable=BooleanVar(
            value=settings.trim_switch_var))
        self.trim_switch.grid(row=0, column=0, padx=20,
                              pady=(10, 5), sticky='nse')

        self.trim_settings_frame = TrimSettingsFrame(
            self, row=1, column=0, settings=settings)

        self.original_label = CTkLabel(
            self, text="Hangfájl:", height=10, font=label_font())
        self.original_label.grid(
            row=2, column=0, padx=20, pady=(10, 2), sticky='sw')
        self.original_textbox = AudioInteractiveTextbox(self.original_audio_manager, audio_load_callback=audio_load_callback,
                                                        selection_changed_callback=self.original_selection_changed,
                                                        audio_play_callback=audio_play_callback, master=self, height=20)
        self.original_textbox.grid(
            row=3, column=0, padx=15, pady=(0, 10), sticky='nsew')

        self.split_label = CTkLabel(
            self, text="Szegmensek:", height=10, font=label_font())
        self.split_label.grid(row=4, column=0, padx=(
            20, 0), pady=(0, 2), sticky='sw')
        self.split_delete_all_button = CTkButton(self, fg_color="transparent", border_width=2, width=30, height=5, text_color=(
            "gray10", "#DCE4EE"), command=self.__delete_all_splitted_content, text="", image=self.delete_all_icon)
        self.split_delete_all_button.grid(
            row=4, column=0, padx=(0, 20), pady=(0, 2), sticky="se")

        self.split_delete_selected_button = CTkButton(self, fg_color="transparent", border_width=2, width=30, height=5, text_color=(
            "gray10", "#DCE4EE"), command=self.__delete_selected_split_content, text="", image=self.trash_icon)
        self.split_delete_selected_button.grid(
            row=4, column=0, padx=(0, 55), pady=(0, 2), sticky="se")

        self.split_textbox = AudioInteractiveTextbox(self.split_audio_manager, audio_load_callback=audio_load_callback,
                                                     selection_changed_callback=self.split_selection_changed,
                                                     audio_play_callback=audio_play_callback, master=self)
        self.split_textbox.grid(row=5, column=0, padx=15,
                                pady=(0, 10), sticky='nsew')

        self.trim_label = CTkLabel(
            self, text="Vágott szegmensek:", height=10, font=label_font())
        self.trim_label.grid(row=6, column=0, padx=20,
                             pady=(0, 2), sticky='sw')
        self.trim_delete_all_button = CTkButton(self, fg_color="transparent", border_width=2, width=30, height=5, text_color=(
            "gray10", "#DCE4EE"), command=self.__delete_all_trimmed_content, text="", image=self.delete_all_icon)
        self.trim_delete_all_button.grid(
            row=6, column=0, padx=(0, 20), pady=(0, 2), sticky="se")

        self.trim_delete_selected_button = CTkButton(self, fg_color="transparent", border_width=2, width=30, height=5, text_color=(
            "gray10", "#DCE4EE"), command=self.__delete_selected_trimmed_content, text="", image=self.trash_icon)
        self.trim_delete_selected_button.grid(
            row=6, column=0, padx=(0, 55), pady=(0, 2), sticky="se")

        self.trim_textbox = AudioInteractiveTextbox(self.trimmed_audio_manager, audio_load_callback=audio_load_callback,
                                                    selection_changed_callback=self.trim_selection_changed,
                                                    audio_play_callback=audio_play_callback, master=self)
        self.trim_textbox.grid(row=7, column=0, padx=15,
                               pady=(0, 10), sticky='nsew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1, minsize=20)
        self.grid_rowconfigure(5, weight=1, minsize=200)
        self.grid_rowconfigure(7, weight=1, minsize=200)

        self.__on_trim_switch_flip()
        self.split_selection_changed()
        self.trim_selection_changed()
        self.update_listboxes()

    def __on_trim_switch_flip(self):
        switched = self.trim_switch.get()
        self.settings.trim_switch_var = switched
        if switched:
            self.trim_settings_frame.grid()
            self.trim_textbox.grid()
            self.trim_label.grid()
            self.trim_delete_all_button.grid()
        else:
            self.trim_settings_frame.grid_remove()
            self.trim_textbox.grid_remove()
            self.trim_label.grid_remove()
            self.trim_delete_all_button.grid_remove()
            self.trim_delete_selected_button.grid_remove()
        for cb in self.trim_switch_flip_callbacks:
            cb(switched)

    def __delete_all_splitted_content(self):
        response = messagebox.askyesno(
            "Törlés", "Biztos törlöd a vágatlan szegmenseket?")
        if response:
            self.audio_stop_callback()
            self.split_audio_manager.delete_all()
            self.split_textbox.clear()

    def __delete_selected_split_content(self):
        if not self.split_textbox.has_selected():
            return
        response = messagebox.askyesno(
            "Törlés", f"Biztos törlöd a kijelölt szegmens(eke)t?")
        if response:
            objects_to_delete = self.split_textbox.selected_object_ids.copy()
            for selected in objects_to_delete:
                audio_file = self.split_audio_manager.get_by_index(selected)
                if audio_file is None:
                    return
                self.audio_stop_callback()
                if self.split_audio_manager.delete_audio_file(audio_file) is not None:
                    self.split_textbox.delete(audio_file.chunk_id)

    def __delete_all_trimmed_content(self):
        response = messagebox.askyesno(
            "Törlés", "Biztosan törlöd a vágott szegmenseket?")
        if response:
            self.audio_stop_callback()
            self.trimmed_audio_manager.delete_all()
            self.trim_textbox.clear()

    def __delete_selected_trimmed_content(self):
        if not self.trim_textbox.has_selected():
            return
        response = messagebox.askyesno(
            "Törlés", f"Biztosan törlöd a kijelölt szegmens(eke)t?")
        if response:
            objects_to_delete = self.trim_textbox.selected_object_ids.copy()
            for selected in objects_to_delete:
                audio_file = self.trimmed_audio_manager.get_by_index(selected)
                if audio_file is None:
                    return
                self.audio_stop_callback()
                if self.trimmed_audio_manager.delete_audio_file(audio_file) is not None:
                    self.trim_textbox.delete(audio_file.chunk_id)

    def on_process_state_change(self, old_process_state: ProcessState, process_state: ProcessState, trim_enabled: bool, forced: bool):
        if process_state is ProcessState.STOPPED:
            self.split_delete_all_button.configure(state=NORMAL)
            self.split_delete_selected_button.configure(state=NORMAL)
            self.trim_delete_all_button.configure(state=NORMAL)
            self.trim_delete_selected_button.configure(state=NORMAL)
            self.trim_switch.configure(state=NORMAL)
            self.trim_settings_frame.set_frame_state(state=NORMAL)
        else:
            self.split_delete_all_button.configure(state=DISABLED)
            self.split_delete_selected_button.configure(state=DISABLED)
            self.trim_delete_all_button.configure(state=DISABLED)
            self.trim_delete_selected_button.configure(state=DISABLED)
            self.trim_switch.configure(state=DISABLED)
            self.trim_settings_frame.set_frame_state(state=DISABLED)

    def split_selection_changed(self):
        if self.split_textbox.has_selected():
            self.split_delete_selected_button.grid()
        else:
            self.split_delete_selected_button.grid_remove()

    def trim_selection_changed(self):
        if self.trim_textbox.has_selected():
            self.trim_delete_selected_button.grid()
        else:
            self.trim_delete_selected_button.grid_remove()

    def original_selection_changed(self):
        pass

    def update_listboxes(self):
        if not self.winfo_exists():
            return
        found = False
        if not self.original_audio_manager.insert_widget_queue.empty():
            audio_file: AudioFile = self.original_audio_manager.insert_widget_queue.get()
            self.original_textbox.insert(audio_file.chunk_id, str(audio_file))
            found = True
        if not self.split_audio_manager.insert_widget_queue.empty():
            audio_file: AudioFile = self.split_audio_manager.insert_widget_queue.get()
            self.split_textbox.insert(audio_file.chunk_id, str(audio_file))
            found = True
        if not self.trimmed_audio_manager.insert_widget_queue.empty():
            audio_file: AudioFile = self.trimmed_audio_manager.insert_widget_queue.get()
            self.trim_textbox.insert(audio_file.chunk_id, str(audio_file))
            found = True
        if found:
            self.after(0, self.update_listboxes)
        else:
            self.after(500, self.update_listboxes)
