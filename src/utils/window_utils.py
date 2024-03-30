from customtkinter import CTkToplevel
from widgets.windows.message_window import MessageWindow
from widgets.windows.plot_window import PlotWindow
from models.environment import get_images_path


def center_window(root: CTkToplevel, width, height):
    """Centers a window
    """
    # Calculate position (considering multi-monitor setups)
    position_right = int(root.winfo_screenwidth()/2 - width/2)
    position_down = int(root.winfo_screenheight()/2 - height/2)

    # Positions the window in the center of the page.
    root.geometry(f"{width}x{height}+{position_right}+{position_down}")


def open_message(parent: CTkToplevel, title: str, message: str):
    if parent.message_window is not None and parent.message_window.winfo_exists():
        parent.message_window.destroy()

    # create window if its None or destroyed
    parent.message_window = MessageWindow(message, master=parent)
    center_window(parent.message_window, 400, 200)
    parent.message_window.title(title)
    parent.message_window.lift()
    parent.message_window.attributes('-topmost', True)


def open_plot(parent: CTkToplevel, audio_manager, audio_file) -> PlotWindow:
    parent.plot_window = PlotWindow(audio_manager, audio_file, master=parent)
    center_window(parent.plot_window, 850, 500)
    parent.plot_window.iconbitmap(f'{get_images_path()}/icon.ico')
    parent.plot_window.title(audio_file.file_path)
    parent.plot_window.lift()
    parent.plot_window.attributes('-topmost', True)
    parent.plot_window.attributes('-topmost', False)
    return parent.plot_window
