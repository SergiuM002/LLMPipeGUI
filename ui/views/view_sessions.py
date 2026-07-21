import customtkinter as ctk
from config.styles import Theme

class ViewSessions(ctk.CTkFrame):
    def __init__(self, controller, master, **kwargs):   
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.master = master
        self.controller = controller
        
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
        
        self.divider = ctk.CTkFrame(self,fg_color=("gray80", "#444444"), height=2)
        self.divider.pack(fill="x", padx=15, pady=20)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.controller.connect_view(self)
        self.controller.load_sessions()
        
    def show_session(self, session):
        session.pack(fill="x", padx=20, pady=10)
        
    # Update widgets and progress after log in
    def update_login(self):
        self.login_text.set("logged in ✓")
            
        self.login_label.update()
        self.login_button.configure(state="disabled")
        
        self.controller.update_sessions_on_login()
                
    
        
    
        