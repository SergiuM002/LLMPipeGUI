import customtkinter as ctk
from llmpipegui.ui.error_popup import ErrorPopup
from llmpipegui.config.styles import Theme

class RemoteInstallWindow(ctk.CTkToplevel):
    """Window for remote installation."""
    def __init__(self, controller, master, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        self.controller = controller
        self.master = master
        
        self.attributes("-topmost", True)
        self.title("Remote Install")

        # Scale the dialog dimensions using the main window's UI scale.
        remote_install_win_width = round(300 * controller.main_ctrl.height_quo)
        remote_install_win_height = round(350 * controller.main_ctrl.height_quo)
        
        win_x = controller.main_ctrl.root.winfo_x()
        win_y = controller.main_ctrl.root.winfo_y()
        win_width = controller.main_ctrl.root.winfo_width()
        win_height = controller.main_ctrl.root.winfo_height()
        
        # Center the dialog over the main application window.
        login_win_x = win_x + round(win_width/2) - round(remote_install_win_width/2)
        login_win_y = win_y + round(win_height/2) - round(remote_install_win_height/2)
        
        self.wm_geometry(f"{remote_install_win_width}x{remote_install_win_height}+{login_win_x}+{login_win_y}")
        self.resizable(False, False)
        
        # Keep the window usable on screens where its contents exceed the window.
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        self.login_text = ctk.StringVar(self.scroll_frame, "not logged in ✕")
        self.login_label = ctk.CTkLabel(
            self.scroll_frame, 
            textvariable=self.login_text,
            font=("Roboto", 17)
        )
        self.login_label.pack(padx=0, pady=45)
        
        logged_in = self.controller.main_ctrl.logged_in

        self.login_button = ctk.CTkButton(
            self.scroll_frame, 
            text="login", 
            state="normal" if not logged_in else "disabled",
            command=controller.show_login_window,
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            font=("Roboto", 18),
            width=180,
            height=40
        )
        self.login_button.pack(padx=5, pady=(5, 40))
        

        self.install_button = ctk.CTkButton(
            self.scroll_frame,
            text="install", 
            state="normal" if logged_in else "disabled",
            command=controller.start_remote_install,
            fg_color=Theme.GREEN_BUTTON,
            text_color=Theme.GREEN_BUTTON_TEXT,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            font=("Roboto", 18),
            width=180,
            height=40
        )
        self.install_button.pack(padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.scroll_frame)
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=self.progress_bar.cget("fg_color"))

        self.progress_text = ctk.StringVar(self.scroll_frame, "")
        self.progress_label = ctk.CTkLabel(self.scroll_frame, textvariable=self.progress_text)
        
        controller.connect_view(self)
        self.protocol("WM_DELETE_WINDOW", lambda: self.self_destroy())
        
    def update_login(self):
        """Enables install button and disables login button after login."""
        self.login_text.set("logged in ✓")
        self.login_label.update()
        self.install_button.configure(state="normal")
        self.login_button.configure(state="disabled")
        
    def show_install_progress_start(self):
        """Sets the progress bar up to show install progress."""
        self.install_button.configure(state="disabled")
        self.progress_bar.pack(padx=30, pady=(30, 0))
        self.progress_bar.update()
        self.progress_label.pack(pady=(5, 0))
        
    def show_install_message(self, progress_text):
        """Shows progress message."""
        self.progress_text.set(progress_text)
        self.progress_label.update()  
        
    def show_install_progress(self, percent: int, first_progress: bool = False):
        """Shows progress percentage."""
        if first_progress:
            self.progress_bar.configure(progress_color=Theme.GREEN_BUTTON) 
        
        self.progress_bar.set(percent/100)
        self.progress_bar.update()
        
    def show_error_text(self):
        """Shows error text."""
        self.progress_text.set("something went wrong")
        self.progress_label.update()
        
    def self_destroy(self):
        """Clean up the reference to this window stored in the main controller and destroy self."""
        self.controller.main_ctrl.remote_install_window = None
        self.destroy()
        
    def show_popup_error(self, message: str):
        """Display an error popup."""
        ErrorPopup(self.controller.main_ctrl.root, self.controller.main_ctrl.height_quo, message)
        
    