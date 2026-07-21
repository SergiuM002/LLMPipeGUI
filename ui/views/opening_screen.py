import customtkinter as ctk
from config.styles import Theme

class OpeningScreen(ctk.CTkFrame):
    def __init__(self, controller, master, **kwargs):   
        super().__init__(master, fg_color="transparent", **kwargs)
        
        sessions_button = ctk.CTkButton(
            self, 
            text="View Sessions",
            command=controller.show_projects_screen,
            height=60,
            font=("Roboto", 22),
            text_color=Theme.GREEN_BUTTON_TEXT,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
        )
        
        sessions_button.pack(fill="x", padx=50, pady=(160, 60))
        
        new_session_button = ctk.CTkButton(
            self, 
            text="New Session",
            command=controller.show_new_project_screen,
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            height=60,
            font=("Roboto", 22),
        )
        
        new_session_button.pack(fill="x", padx=50, pady=(0, 50))
        
        
