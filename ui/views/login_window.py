import customtkinter as ctk
from ui.error_popup import ErrorPopup
from config.styles import Theme

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, controller, master, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.controller = controller
        self.master = master
        
        self.attributes("-topmost", True)
        self.title("Login")
        
        login_win_width = round(300 * controller.main_ctrl.height_quo)
        login_win_height = round(350 * controller.main_ctrl.height_quo)
        
        win_x = controller.main_ctrl.root.winfo_x()
        win_y = controller.main_ctrl.root.winfo_y()
        win_width = controller.main_ctrl.root.winfo_width()
        win_height = controller.main_ctrl.root.winfo_height()
        
        login_win_x = win_x + round(win_width/2) - round(login_win_width/2)
        login_win_y = win_y + round(win_height/2) - round(login_win_height/2)
        
        self.wm_geometry(f"{login_win_width}x{login_win_height}+{login_win_x}+{login_win_y}")
        self.resizable(False, False)
        
        
        self.login_scrollframe = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.login_scrollframe.pack(fill="both", expand=True)
        
        self.server_label = ctk.CTkLabel(self.login_scrollframe, text="Server", font=("Roboto", 20), text_color=("gray20", "white"))
        self.server_label.pack(pady=(20, 0))
        
        self.server_entry = ctk.CTkEntry(self.login_scrollframe, font=("Roboto", 16), height=28, text_color=("gray20", "white"))
        self.server_entry.pack(fill="x", padx=20)
        controller.main_ctrl.root.after(100, self.server_entry.focus_force)

        self.username_label = ctk.CTkLabel(self.login_scrollframe, text="Username", font=("Roboto", 20), text_color=("gray20", "white"))
        self.username_label.pack(pady=(20, 0))
        
        self.username_entry = ctk.CTkEntry(self.login_scrollframe, font=("Roboto", 16), height=28, text_color=("gray20", "white"))
        self.username_entry.pack(fill="x", padx=20)
        
        self.password_label = ctk.CTkLabel(self.login_scrollframe, text="Password", font=("Roboto", 20), text_color=("gray20", "white"))
        self.password_label.pack(pady=(20, 0))
        
        self.password_entry = ctk.CTkEntry(self.login_scrollframe, font=("Roboto", 16), show="*", height=28, text_color=("gray20", "white"))
        self.password_entry.pack(fill="x", padx=20)
        
        self.confirm_button = ctk.CTkButton(
            self.login_scrollframe, 
            text="Login", 
            font=("Roboto", 20), 
            command=lambda: self.confirm_button_clicked(),
            height=32,   
            fg_color=(Theme.GREEN_BUTTON, Theme.GREEN_BUTTON),
            text_color=("white"),
            hover_color=(Theme.GREEN_BUTTON_HOVER, Theme.GREEN_BUTTON_HOVER)
        )
        self.confirm_button.pack(anchor=ctk.CENTER, padx=10, pady=40)
        
        controller.autofill_saved_info(self)
        
        self.bind_all("<Return>", lambda e: self.confirm_button_clicked())
        
        self.protocol("WM_DELETE_WINDOW", lambda: self.delete_self())
        
    def fill_saved_info(self, login_info):
        self.server_entry.insert(0, login_info["server"])
        self.username_entry.insert(0, login_info["username"])
        self.controller.main_ctrl.root.after(100, self.password_entry.focus_force)
        
    def enable_confirm_button(self):
        self.confirm_button.configure(state="normal")
        self.confirm_button.update()
        
    def disable_confirm_button(self):
        self.confirm_button.configure(state="disabled")
        self.confirm_button.update()
        
    def confirm_button_clicked(self):
        self.unbind_all("<Return>")
        self.disable_confirm_button()
        
        self.controller.confirm_login(self)    
        
    def show_fields_error_message_box(self):
        scaling = self.controller.main_ctrl.height_quo
        self.msg_box = ErrorPopup(self.controller.main_ctrl.root, scaling, "Please fill out all the fields.")

        self.msg_box.bind("<Destroy>", lambda e: self.controller.clean_msg_box_bindings(e, self))   
        
        self.confirm_button.configure(state="normal") 
        
    def show_input_error_message_box(self, message):
        scaling = self.controller.main_ctrl.height_quo
        self.msg_box = ErrorPopup(self.controller.main_ctrl.root, scaling, message)
        self.msg_box.bind("<Destroy>", lambda e: self.controller.clean_msg_box_bindings(e, self))   
        
        self.confirm_button.configure(state="normal") 
    
    # Scroll logic
    def login_scroll(self, event, dist):            
        current_pos = self.login_scrollframe._parent_canvas.yview()[0]
        
        step = 0.02
        
        if dist > 0:
            new_pos = current_pos + step
        else:
            new_pos = current_pos - step
        
        self.login_scrollframe._parent_canvas.yview_moveto(max(new_pos, 0))
        
    def delete_self(self):
        self.unbind_all("<Return>")
        self.destroy()