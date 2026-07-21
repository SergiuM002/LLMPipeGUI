import subprocess
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from config.styles import Theme
import config.environment as env

class SessionTab(ctk.CTkFrame):
    def __init__(self, controller, master, **kwargs):   
        
        super().__init__(master, fg_color=("gray88", "#2A2A2A"), **kwargs)
        
        self.controller = controller
        self.master = master
        
        
        self.info_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        
        self.info_frame.pack(side=ctk.LEFT)
        
        self.project_label = ctk.CTkLabel(
            self.info_frame,
            text=controller.session_name,
            font=("Roboto", 18),
            text_color=("gray20", "white")
        )
        
        self.project_label.pack(anchor=ctk.W, padx=20, pady=(20, 0))
        
        self.progress_frame = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent"
        )
        
        self.progress_frame.pack(anchor=ctk.W, padx=20, pady=20)
        
        self.progress_text = ctk.StringVar(self.info_frame, "starting model...")
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            textvariable=self.progress_text,
            font=("Roboto", 13),
            text_color=("gray20", "white")
        )
        
        self.progress_label.pack(side=ctk.LEFT, padx=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            progress_color=Theme.GREEN_BUTTON
        )
        
        self.progress_bar.set(0)
        self.progress_bar.pack(side=ctk.LEFT)
        
        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        
        self.button_frame.pack(side=ctk.RIGHT, padx=20, pady=20)
        
        self.get_file_button = ctk.CTkButton(
            self.button_frame,
            text="Get Files",
            font=("Roboto", 14),
            text_color=Theme.GREEN_BUTTON_TEXT,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            state="disabled",
            command=self.get_file_button_clicked
        )
        
        self.get_file_button.pack(anchor=ctk.E, pady=10)
        
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Delete",
            font=("Roboto", 14),
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            state="disabled",
            command=self.delete_button_clicked
        )
        
        self.delete_button.pack(anchor=ctk.E, pady=10)
        
        self.controller.set_session_state(self)
        
    def show_session_state_start(self):
        self.delete_button.configure(state="normal")
        
    def show_session_state_in_progress(self, sequence_progress, sequence_count, progress):
        self.project_label.configure(text_color="#D6C851")
        self.progress_bar.configure(progress_color="#D6C851")
        self.progress_bar.set(progress)
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | {round(progress*100)}%")
        
    def show_session_state_sequence_finished(self, sequence_progress, sequence_count):
        self.progress_bar.pack_forget()
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | processing data...")
        self.project_label.configure(text_color="#D6C851")
        
    def show_session_state_finished(self):
        self.progress_bar.pack_forget()
        self.progress_text.set("done.")
        
    def pack_progress_bar(self):
        self.progress_bar.pack(side=ctk.LEFT)
    
    def update_percentage_progress(self, sequence_progress, sequence_count, percentage, progress):
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | {percentage}\r")
        self.progress_bar.set(progress)
        self.progress_label.update()
        
    def update_processing_progress(self, sequence_progress, sequence_count):
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | processing data...")
        self.progress_bar.pack_forget() 
        self.progress_label.update()
        
    def update_finished_progress(self):
        self.progress_bar.destroy()
        self.progress_text.set("done.")
        self.get_file_button.configure(state="normal")
        self.progress_label.update()
        
    def on_login_config(self):
        self.progress_bar.configure(progress_color=Theme.GREEN_BUTTON)
        self.project_label.configure(text_color=("gray20", "white"))
        self.delete_button.configure(state="normal")
    
    def get_file_button_clicked(self):
        output_path = ""
        
        if env.OPERATING_SYSTEM == "Linux":
            try:
                output_path = subprocess.check_output(
                    ['zenity', '--file-selection', '--title=Select a  Path', '--directory'],
                    stderr=subprocess.STDOUT
                ).decode('utf-8').strip()
                output_path = output_path.splitlines()[-1]
            except subprocess.CalledProcessError:
                return None
        else:
            output_path = filedialog.askdirectory(title="Select a path")
            
        self.controller.get_files(output_path)
        
    def delete_button_clicked(self):
        self.controller.confirm_delete(self)
            
    def get_delete_confirmation(self, message):
        scaling = self.controller.main_ctrl.height_quo
        msg_box = CTkMessagebox(
            master=self.controller.main_ctrl.root,
            title="Are you sure?",
            message=message,
            icon="question",
            option_1="Cancel",
            option_2="Yes",
            width=int(400*scaling),
            height=int(200*scaling),
            button_width=(130*scaling),
            button_height=(40*scaling),
            button_color=(Theme.GREEN_BUTTON, Theme.GRAY_BUTTON),
            button_hover_color=Theme.GRAY_BUTTON_HOVER
        )
        
        return msg_box.get()
    
    def delete_self(self):
        self.pack_forget()
        self.destroy()
        