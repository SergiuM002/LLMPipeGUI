import subprocess
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from config.styles import Theme
import config.environment as env
from tkinter import TclError
from ui.error_popup import ErrorPopup

class SessionTab(ctk.CTkFrame):
    """Display session status, progress, and session-related controls."""

    def __init__(self, controller, master, **kwargs):   
        """Create the tab and initialize its status display and controls."""
        
        super().__init__(master, fg_color=("gray88", "#2A2A2A"), **kwargs)
        
        self.controller = controller
        self.master = master
        
        
        # Keep session details and progress together on the left side
        self.info_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.info_frame.pack(side=ctk.LEFT)
        
        self.username_server_label = ctk.CTkLabel(
            self.info_frame,
            text=f"{controller.user}@{controller.server}",
            font=("Roboto", 14),
            text_color=("gray20", "white")
        )
        self.username_server_label.pack(anchor=ctk.W, padx=20, pady=(10, 0))
        
        self.session_label = ctk.CTkLabel(
            self.info_frame,
            text=controller.session_name,
            font=("Roboto", 18),
            text_color=("gray20", "white")
        )
        self.session_label.pack(anchor=ctk.W, padx=20, pady=(10, 0))
        
        self.progress_frame = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent"
        )
        self.progress_frame.pack(side=ctk.LEFT, padx=20, pady=20)
              
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            progress_color=Theme.GREEN_BUTTON
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(anchor=ctk.W)
        
        self.progress_text = ctk.StringVar(self.info_frame, "starting model...")
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            textvariable=self.progress_text,
            font=("Roboto", 13),
            text_color=("gray20", "white")
        )
        self.progress_label.pack(anchor=ctk.W, padx=(0, 10))
        
        self.time_remaining = ctk.StringVar(self.progress_frame, "Sequence ETA: --")
        self.time_remaining_label = ctk.CTkLabel(
            self.progress_frame, 
            textvariable=self.time_remaining,
            font=("Roboto", 13),
            text_color=("gray20", "white")
        )
        self.time_remaining_label.pack(anchor=ctk.W)
        
        # Actions are grouped on the right and enabled only for logged-in users
        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )    
        self.button_frame.pack(side=ctk.RIGHT, padx=20, pady=20)
        
        logged_in = controller.logged_in_to_server_with_user(self.controller.server, self.controller.user)
        
        self.get_file_button = ctk.CTkButton(
            self.button_frame,
            text="Get Files",
            font=("Roboto", 14),
            text_color=Theme.GREEN_BUTTON_TEXT,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            state="normal" if logged_in else "disabled",
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
            state="normal" if logged_in else "disabled",
            command=self.delete_button_clicked
        )
        
        self.delete_button.pack(anchor=ctk.E, pady=10)
        
        self.controller.set_session_state(self)
        
    def call_live_progress_update(self, func, *args):
        """Run a UI update and stop progress callbacks if the widget is gone."""
        try:
            func(*args)
        except TclError:
            self.controller.stop_event.set()
        
    def show_session_state_start(self):
        """Enable deletion once session startup has begun."""
        self.delete_button.configure(state="normal")
        
    def show_session_state_in_progress(self, sequence_progress, sequence_count, progress):
        """
        Display the current sequence progress and show the color indicating
        that the session is unsynced with the actual server progress.
        """
        self.time_remaining_label.pack_forget()
        self.session_label.configure(text_color="#D6C851")
        self.progress_bar.configure(progress_color="#D6C851")
        self.progress_bar.set(progress)
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | {round(progress*100)}%")
        
    def show_session_state_sequence_finished(self, sequence_progress, sequence_count):
        """
        Replace the progress bar with a data-processing status and show the color 
        indicating that the session is unsynced with the actual server progress.
        """
        self.time_remaining_label.pack_forget()
        self.progress_bar.pack_forget()
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | processing data...")
        self.session_label.configure(text_color="#D6C851")
        
    def show_session_state_finished(self):
        """Show the completed state and hide no-longer-relevant indicators."""
        self.time_remaining_label.pack_forget()
        self.progress_bar.pack_forget()
        self.progress_text.set("done.")
        
    def pack_progress_bar(self):
        """Make the progress bar visible again."""
        self.progress_bar.pack()
        
    def pack_time_remaining_label(self):
        """Show the sequence ETA label."""
        self.time_remaining_label.pack(anchor=ctk.W)
    
    def update_percentage_progress(self, sequence_progress, sequence_count, percentage, progress):
        """Update the displayed percentage and progress-bar value."""
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | {percentage}%\r")
        self.progress_bar.set(progress)
        self.progress_label.update()
        
    def update_eta(self, eta):
        """Refresh the estimated time remaining for the current sequence."""
        self.time_remaining.set(f"Sequence ETA: {eta}")
        
    def update_processing_progress(self, sequence_progress, sequence_count):
        """Show processing status while hiding the progress bar."""
        self.progress_text.set(f"{sequence_progress}/{sequence_count} | processing data...")
        self.progress_bar.pack_forget() 
        self.progress_label.update()
        
    def update_finished_progress(self):
        """Show completion and enable file retrieval."""
        self.time_remaining_label.pack_forget()
        self.progress_bar.pack_forget() 
        self.progress_text.set("done.")
        self.get_file_button.configure(state="normal")
        self.progress_label.update()
        
    def on_login_config(self):
        """
        Show the colors that indicate that the session is synced
        and enable deletion after login.
        """
        self.progress_bar.configure(progress_color=Theme.GREEN_BUTTON)
        self.session_label.configure(text_color=("gray20", "white"))
        self.delete_button.configure(state="normal")
    
    def get_file_button_clicked(self):
        """Prompt for a destination directory and start retrieving session files."""
        output_path = ""
        
        if env.OPERATING_SYSTEM == "Linux":
            # Use Zenity on Linux; cancellation leaves the session unchanged.
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
            
        self.controller.get_files(self, output_path)
        
    def delete_button_clicked(self):
        """Delegate the session deletion to the controller."""
        self.controller.confirm_delete(self)
            
    def get_confirmation(self, message):
        """Show a confirmation dialog and return the selected option."""
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

    def show_popup_error(self, message):
        """Display an error popup."""
        ErrorPopup(self.controller.main_ctrl.root, self.controller.main_ctrl.height_quo, message)
    
    def delete_self(self):
        """Remove this tab from its parent and destroy its widgets."""
        self.pack_forget()
        self.destroy()
        