from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage, CTkEntry, StringVar, END
from utils.fonts import label_font
from utils.general_utils import search_in_text
from widgets.interactive_textbox import ResultInteractiveTextbox
from managers.result_manager import ResultManager
from managers.audio_file_manager import TrimmedAudioFileManager, SplitAudioFileManager
from models.result_row import ResultRow
from models.environment import get_images_path
from models.process_state import ProcessState
from models.settings import Settings


class ResultPreviewFrame(CTkFrame):
    def __init__(self, parent, row, column, settings: Settings, result_manager: ResultManager, split_audio_file_manager: SplitAudioFileManager, trimmed_audio_file_manager: TrimmedAudioFileManager, audio_load_callback, audio_play_callback):
        super().__init__(parent)
        self.settings = settings
        self.result_manager: ResultManager = result_manager

        from PIL import Image
        self.delete_all_icon = CTkImage(Image.open(
            f'{get_images_path()}/delete_all.png'), size=(17, 17))
        self.arrow_up_icon = CTkImage(Image.open(
            f'{get_images_path()}/arrow_up.png'), size=(17, 17))
        self.arrow_down_icon = CTkImage(Image.open(
            f'{get_images_path()}/arrow_down.png'), size=(17, 17))

        self.grid(row=row, column=column, pady=20, sticky="swne")

        # create textbox
        self.result_preview_label = CTkLabel(
            self, text="Előnézet:", height=10, font=label_font())
        self.result_preview_label.grid(
            row=0, pady=(10, 10), padx=10, sticky="ws")

        self.search_label = CTkLabel(
            self, text="Keresés:", height=10, font=label_font())
        self.search_label.grid(row=0, padx=395, pady=(10, 5), sticky="se")

        self.search_entry_var = StringVar()
        self.search_entry_var.trace_add("write", self.on_search_text_changed)
        self.search_entry = CTkEntry(
            self, height=10, font=label_font(), textvariable=self.search_entry_var)
        self.search_entry.grid(row=0, padx=250, pady=(10, 0), sticky="se")

        self.search_result_label = CTkLabel(
            self, text="0/", height=10, font=label_font())
        self.search_result_label.grid(
            row=0, padx=205, pady=(10, 5), sticky="se")

        self.search_by_value_entry_val = StringVar(value="0")
        self.search_by_value_entry_val.trace_add(
            "write", self.__go_to_searched_text)
        self.search_by_value_entry = CTkEntry(self, width=50, height=10, font=label_font(
        ), textvariable=self.search_by_value_entry_val)
        self.search_by_value_entry.grid(
            row=0, padx=150, pady=(10, 0), sticky="se")

        self.down_button = CTkButton(self, fg_color="transparent", text="", corner_radius=100,
                                     width=5, height=5, image=self.arrow_down_icon, command=self.__go_to_next)
        self.down_button.grid(row=0, padx=120, pady=(25, 0), sticky="se")

        self.up_button = CTkButton(self, fg_color="transparent", text="", corner_radius=100,
                                   width=5, height=5, image=self.arrow_up_icon, command=self.__go_to_previous)
        self.up_button.grid(row=0, padx=95, pady=(25, 0), sticky="se")

        self.delete_button = CTkButton(self, fg_color="transparent", border_width=2, width=50, height=5, text_color=(
            "gray10", "#DCE4EE"), command=self.__delete_all_results, text="", image=self.delete_all_icon)
        self.delete_button.grid(row=0, padx=15, pady=(10, 0), sticky="se")

        self.textbox = ResultInteractiveTextbox(result_manager=result_manager,
                                                master=self,
                                                trimmed_audio_file_manager=trimmed_audio_file_manager,
                                                split_audio_file_manager=split_audio_file_manager,
                                                audio_load_callback=audio_load_callback,
                                                audio_play_callback=audio_play_callback,
                                                selection_changed_callback=self.selection_changed,
                                                height=350)
        self.textbox.grid(row=1, pady=(5, 5), padx=10, sticky="wsne")

        self.textbox.tag_config("search_tag", background="yellow")
        self.textbox.tag_config("selected_search_tag", background="#FFA500")
        self.__search_results = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=10)
        self.grid_rowconfigure(1, weight=1, minsize=300)

        self.update_textbox()

    def __delete_all_results(self):
        response = messagebox.askyesno(
            "Törlés", "Biztos törlöd a összes feldolgozott szöveget?")
        if response:
            self.__search_results = []
            self.search_entry_var.set('')
            self.search_by_value_entry_val.set('0')
            self.result_manager.delete_all()
            self.textbox.clear()

    def on_process_state_change(self, old_process_state: ProcessState, process_state: ProcessState, trim_enabled: bool, forced: bool):
        if process_state is ProcessState.STOPPED:
            self.delete_button.configure(state="normal")
        else:
            self.delete_button.configure(state="disabled")

    def selection_changed(self):
        pass

    def on_search_text_changed(self, *args):
        self.textbox.tag_remove("search_tag", "1.0", END)
        self.textbox.tag_remove("selected_search_tag", "1.0", END)
        pattern = self.search_entry.get()
        if pattern != "":
            indexes = []
            for i in range(1, int(self.textbox.index(END).split(".")[0]) - 1):
                for j in search_in_text(text=self.textbox.get(f"{i}.0", f"{i+1}.0"), pattern=pattern):
                    indexes.append((f"{i}.{j}", f"{i}.{j + len(pattern)}"))

            if indexes != []:
                for i, j in indexes:
                    self.textbox.tag_add("search_tag", i, j)

                self.search_result_label.configure(text=f"{len(indexes)}/")
                self.__search_results = indexes
                self.search_by_value_entry_val.set("1")
                return

        self.search_result_label.configure(text="0/")
        self.search_by_value_entry_val.set("0")
        self.__search_results = []

    def __go_to_next(self):
        if len(self.__search_results) == 0:
            self.search_by_value_entry_val.set('0')
            return
        new_value = int(self.search_by_value_entry_val.get()) + 1
        if new_value > len(self.__search_results):
            new_value = 1
        self.search_by_value_entry_val.set(str(new_value))

    def __go_to_previous(self):
        if len(self.__search_results) == 0:
            self.search_by_value_entry_val.set('0')
            return
        new_value = int(self.search_by_value_entry_val.get()) - 1
        if new_value < 1:
            new_value = len(self.__search_results)
        self.search_by_value_entry_val.set(str(new_value))

    def __go_to_searched_text(self, *args):
        if self.__search_results != []:
            self.textbox.tag_remove("selected_search_tag", "1.0", END)
            new_value = int(self.search_by_value_entry_val.get(
            )) - 1 if self.search_by_value_entry_val.get().isdecimal() else -1
            if new_value >= 0 or new_value < len(self.__search_results):
                new_range = self.__search_results[new_value]
                self.textbox.tag_add("selected_search_tag",
                                     new_range[0], new_range[1])
                self.textbox.see(new_range[0])

    def update_textbox(self):
        if not self.winfo_exists():
            return
        found = False
        if not self.result_manager.insert_widget_queue.empty():
            result: ResultRow = self.result_manager.insert_widget_queue.get()
            self.textbox.insert(result.id, result.sentence)
            self.on_search_text_changed()
            found = True
        if found:
            self.after(0, self.update_textbox)
        else:
            self.after(1000, self.update_textbox)
