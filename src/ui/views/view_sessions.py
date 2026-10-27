import customtkinter as ctk
from config.styles import Theme

class ViewSessions(ctk.CTkFrame):
    """Display sessions and provide navigation, login, and sync controls."""

    def __init__(self, controller, master, **kwargs):   
        """Create the sessions view and initialize its controls."""
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.master = master
        self.controller = controller
        
        # Keep navigation and login status together in the top row
        self.button_frame1 = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame1.pack(fill="x", padx=20, pady=(20, 0))
        
        self.back_button = ctk.CTkButton(
            self.button_frame1,
            height=30,
            text="Back",
            font=("Roboto", 15),
            text_color=Theme.GREEN_BUTTON_TEXT,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            command=controller.main_ctrl.show_opening_screen
        )
        self.back_button.pack(side=ctk.LEFT)
        
        self.login_text = ctk.StringVar(self.button_frame1, "not logged in ✕")
            
        self.login_label = ctk.CTkLabel(
            self.button_frame1, 
            textvariable=self.login_text, 
            font=("Roboto", 13),
            text_color=("gray20", "white")
        )
        self.login_label.pack(side=ctk.RIGHT)
        
        self.login_button = ctk.CTkButton(
            self.button_frame1, 
            height=30, 
            text="login", 
            font=("Roboto", 15),
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            command=lambda: controller.show_login_window(self)
        )
        self.login_button.pack(side=ctk.RIGHT, padx=(0, 15))
        
        # Session actions are enabled after the user logs in
        self.button_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame2.pack(fill="x", padx=20, pady=(20, 5))
        
        self.refresh_button = ctk.CTkButton(
            self.button_frame2,
            height=30,
            text="Sync Sessions", 
            font=("Roboto", 15),
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            command=controller.refresh_sessions,
            state="disabled"
        )
        self.refresh_button.pack(side=ctk.LEFT)
        
        self.only_synced_checkbox = ctk.CTkCheckBox(
            self.button_frame2,
            text="Show only synced sessions",
            font=("Roboto", 15),
            checkbox_height=24,
            checkbox_width=24,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            border_color=("gray45", "gray55"),
            text_color=Theme.GENERAL_LABEL,
            command=controller.toggle_only_synced,
            state="disabled"
        )
        self.only_synced_checkbox.pack(side=ctk.LEFT, padx=10)
        
        # Session widgets are displayed in this scrollable area
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
                
        self.controller.connect_view(self)
        self.controller.load_sessions()
        
    def show_session(self, session):
        """Pack a session widget into the scrollable session list."""
        session.pack(fill="x", padx=20, pady=10)
        
    def update_login(self):
        """Reflect successful login and refresh the available sessions."""
        self.login_text.set("logged in ✓")
            
        self.login_label.update()
        self.login_button.configure(state="disabled")
        self.refresh_button.configure(state="normal")
        self.only_synced_checkbox.configure(state="normal")
        
        self.controller.refresh_sessions()
        
                
    
        
    
        