from abc import ABC, abstractmethod
from typing import Optional
from customtkinter import CTkTextbox, END, CURRENT, NONE
from utils.fonts import textbox_font, blue_theme_color
from managers.result_manager import ResultManager
from managers.audio_file_manager import AudioFileManager, SplitAudioFileManager, TrimmedAudioFileManager
from models.audio_file import AudioFile

class InteractiveTextbox(CTkTextbox, ABC):
    def __init__(self, master, audio_load_callback, audio_play_callback, selection_changed_callback, width=200, height=200):
        super().__init__(master, width=width, height=height, font=textbox_font(), text_color='black', fg_color='#D3D3D3', wrap=NONE)
        self.audio_load_callback = audio_load_callback
        self.audio_play_callback = audio_play_callback
        self.selection_changed_callback = selection_changed_callback

        self.row_object_map = list()
        self.selected_object_ids : list[int] = []

        self.selected_tag = 'selected_tag'
        self.tag_config(self.selected_tag, background="#999999")
        self.bind("<Button-1>", command=self.on_text_click)
        self.bind('<Control-Button-1>', command=self.on_ctrl_click)
        self.bind("<Double-1>", command=self.on_text_double_click)

        self.cursor_tag = 'cursor_tag'
        self.tag_config(self.cursor_tag, background=blue_theme_color)

        self.configure(state="disabled")

    def on_text_click(self, event):
        current_row_id = self.__get_clicked_row() - 1
        if current_row_id >= self.row_count():
            return
        if self.has_selected() and self.row_object_map[current_row_id] in self.selected_object_ids:
            self.unselect_all()
            return
        self.unselect_all()
        self.selected_object_ids.append(self.row_object_map[current_row_id])
        self._load_file(self.selected_object_ids[0])
        self.tag_add(self.selected_tag, f'{current_row_id + 1}.0', f'{current_row_id + 1}.end')
        self.selection_changed_callback()

    def on_ctrl_click(self, event):
        current_row_id = self.__get_clicked_row() - 1
        if current_row_id >= self.row_count():
            return
        if self.has_selected() and self.row_object_map[current_row_id] in self.selected_object_ids:
            self.unselect(current_row_id)
            return
        self.selected_object_ids.append(self.row_object_map[current_row_id])
        self.tag_add(self.selected_tag, f'{current_row_id + 1}.0', f'{current_row_id + 1}.end')
        self.selection_changed_callback()

    def _find(self, object_id : int) -> Optional[int]:
        if object_id in self.row_object_map:
            return self.row_object_map.index(object_id)
        return None

    def unselect_all(self):
        self.tag_remove(self.selected_tag, '1.0', END)
        self.tag_remove(self.cursor_tag, '1.0', END)
        self.selected_object_ids.clear()
        self.selection_changed_callback()

    def unselect(self, current_row_id):
        if current_row_id >= self.row_count():
            return
        self.tag_remove(self.selected_tag, f'{current_row_id + 1}.0', f'{current_row_id + 1}.end')
        self.tag_remove(self.cursor_tag, f'{current_row_id + 1}.0', f'{current_row_id + 1}.end')
        self.selected_object_ids.remove(self.row_object_map[current_row_id])
        self.selection_changed_callback()

    @abstractmethod
    def _load_file(self, object_id):
        pass

    def __get_clicked_row(self) -> int:
        return int(self.index(CURRENT).split('.')[0])

    def on_text_double_click(self, event):
        self.on_text_click(event)
        self.audio_play_callback()

    def insert(self, object_id : int, text : str):
        if object_id in self.row_object_map:
            return
        self.configure(state='normal')
        row_id = self.row_count()
        if len(self.row_object_map) == 0 or self.row_object_map[-1] > object_id:       
            for i, obj in enumerate(self.row_object_map):
                if obj > object_id:
                    row_id = i
                    break

        super().insert(f'{row_id + 1}.0', text + '\n')
        self.row_object_map.insert(row_id, object_id)
        self.configure(state='disabled')

    def delete(self, object_id : int):
        row_id = self._find(object_id)
        if row_id is None:
            return
        self.configure(state='normal')
        start_index = f'{row_id + 1}.0'
        end_index = f'{row_id + 2}.0'
        super().delete(start_index, end_index)
        self.row_object_map.remove(object_id)
        self.configure(state='disabled')

    def clear(self):
        self.configure(state='normal')
        super().delete('1.0', END)
        self.row_object_map.clear()
        self.configure(state='disabled')


    def row_count(self):
        return len(self.row_object_map)
    
    def has_selected(self) -> bool:
        return len(self.selected_object_ids) != 0


class AudioInteractiveTextbox(InteractiveTextbox):
    def __init__(self, audio_file_manager : AudioFileManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_file_manager : AudioFileManager = audio_file_manager

    def _load_file(self, object_id):
        if object_id > self.audio_file_manager.size() - 1:
            return
        audio_file = self.audio_file_manager.get_by_index(object_id)
        self.audio_load_callback(self.audio_file_manager, audio_file)

class ResultInteractiveTextbox(InteractiveTextbox):
    def __init__(self, result_manager : ResultManager, split_audio_file_manager: SplitAudioFileManager,
                 trimmed_audio_file_manager : TrimmedAudioFileManager,
                  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result_manager : ResultManager = result_manager
        self.split_audio_file_manager = split_audio_file_manager
        self.trimmed_audio_file_manager = trimmed_audio_file_manager

        self.configure(state="normal")

    def _load_file(self, object_id): 
        result = self.result_manager.get_by_id(object_id)
        if result is None:
            return
        if 'split' in result.chunk_file:
            audio_file_manager = self.split_audio_file_manager
        elif 'trim' in result.chunk_file:
            audio_file_manager = self.trimmed_audio_file_manager
        else:
            return
        audio_file = audio_file_manager.get_audio_by_result(result)
        self.audio_load_callback(audio_file_manager, audio_file, result)

    def refresh_cursor_position(self, audio_file : Optional[AudioFile], elapsed_time : float):
        self.tag_remove(self.cursor_tag, '1.0', END)
        if audio_file is None:
            return
        result = self.result_manager.get_result_by_audio(audio_file, elapsed_time)
        if result is None:
            return
        row_id = self._find(result.id)
        if row_id is None:
            return
        ratio = (elapsed_time - result.relative_timestamp[0]) / (result.relative_timestamp[1] - result.relative_timestamp[0])
        char_index = round(ratio * len(result.sentence))
        end_index = int(self.index(f"{row_id + 1}.end").split('.')[1])
        if char_index > end_index:
            char_index_str = str(max(end_index - 1, 0))
        else:
            char_index_str = str(max(char_index - 1, 0))
        self.tag_add(self.cursor_tag, f'{row_id + 1}.{char_index_str}', f'{row_id + 1}.{char_index_str} +1c')
        self.see(f"{self.cursor_tag}.first")
        