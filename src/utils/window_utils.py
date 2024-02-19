from screeninfo import get_monitors
from windows.message_window import MessageWindow
from customtkinter import CTkToplevel

def center_window(root : CTkToplevel):
    """Centers a window
    """
    # Gets the requested values of the height and width.
    window_width = root._current_width
    window_height = root._current_height
    
    # Get monitor information
    monitors = get_monitors()
    primary_monitor = monitors[0]  # Consider the first monitor as primary
    
    # Calculate position (considering multi-monitor setups)
    position_right = primary_monitor.x + int(primary_monitor.width/2 - window_width/2)
    position_down = primary_monitor.y + int(primary_monitor.height/2 - window_height/2)
    
    # Positions the window in the center of the page.
    root.geometry(f"+{position_right}+{position_down}")

def open_message(parent : CTkToplevel, title : str, message : str):        
    """Opens a top-level window with the given title and message, used to display information to the user.

    Args:
        - title (str): The title of the top-level window.
        - message (str): The message to display in the top-level window.
    """
    if parent.message_window is not None and parent.message_window.winfo_exists():
        parent.message_window.destroy()
    
    parent.message_window = MessageWindow(message, parent)  # create window if its None or destroyed
    parent.message_window.title(title)       
    center_window(parent.message_window)
    parent.message_window.lift()
    parent.message_window.attributes('-topmost', True)