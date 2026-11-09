import customtkinter as ctk
from llmpipegui.config.styles import Theme

class OpeningScreen(ctk.CTkFrame):
    """Opening screen controlled by its controller."""
    def __init__(self, controller, master, **kwargs):   
        super().__init__(master, fg_color="transparent", **kwargs)
        
        sessions_button = ctk.CTkButton(
            self, 
            text="View Sessions",
            command=controller.show_sessions_screen,
            height=60,
            font=("Roboto", 22),
            text_color=Theme.GREEN_BUTTON_TEXT,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
        )
        sessions_button.pack(fill="x", padx=50, pady=(150, 40))
        
        new_session_button = ctk.CTkButton(
            self, 
            text="New Session",
            command=controller.show_new_session_screen,
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            height=60,
            font=("Roboto", 22),
        )
        new_session_button.pack(fill="x", padx=50, pady=(0, 40))
        
        remote_install_button = ctk.CTkButton(
            self, 
            text="Remote Install",
            command=controller.show_remote_install_window,
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            height=60,
            font=("Roboto", 22),
        )
        remote_install_button.pack(fill="x", padx=50, pady=(0, 50))
        
        
