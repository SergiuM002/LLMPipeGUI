import customtkinter as ctk
from tkinter import font as tkfont
from screeninfo import get_monitors
from ui.views.session_creation import CreateSession 
from ui.views.opening_screen import OpeningScreen
from ui.views.view_sessions import ViewSessions
from controllers.views.session_creation_controller import CreateSessionController 
from controllers.views.opening_screen_controller import OpeningScreenController 
from controllers.views.view_sessions_controller import ViewSessionsController 
from controllers.ssh_controller import SSHController
import controllers.json_controller as json_controller
from ui.error_popup import ErrorPopup
from collections import defaultdict
from pathlib import Path
import re
import shlex

class MainController:
    """Coordinates the application's main window, views, and session state."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.withdraw() # Hide window so the user does not see everything loading
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.title("LLMPipeGUI")
        self.root.resizable(False, False)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        
        self.current_monitor = get_monitors()[0]

        for m in get_monitors():
            if m.is_primary:
                self.current_monitor = m
                
        self.ssh_controller = SSHController(self)
        self.logged_in = False
        self.server = ""
        self.user = ""
        self.height_quo = self.current_monitor.height/1200 # Used to track the size of the monitor

        self.original_window_height = 545
        self.original_window_width = 545
        
        self.current_window_height = self.original_window_height
        self.current_window_width = self.original_window_width

        self.root.wm_geometry("")

        self.root.geometry(f"{round(self.original_window_width*self.height_quo)}x{round(self.original_window_height*self.height_quo)}")

        self.views = {}
        
        self.session_ctrls = []
        self.session_views = []
        
        self.all_sessions_info = json_controller.load_all_sessions_info()
        self.all_sessions_info.sort(
            key=lambda info: (
                info["user"] != self.user or info["server"] != self.server,
                f"{info["user"]}@{info["server"]}",
                self._natural_sort_key(info["name"]),
            )
        )
        self.synced_sessions_info = []
        
        self.root.after(200, self.resize_window, self.root, self.current_monitor)
        
        self.opening_screen_ctrl = OpeningScreenController(self)
        self.opening_screen_view = OpeningScreen(self.opening_screen_ctrl, self.root)
        
        self.view_sessions_ctrl = ViewSessionsController(self)
        self.view_sessions_view = ViewSessions(self.view_sessions_ctrl, self.root)
        
        self.create_session_ctrl = CreateSessionController(self)
        self.create_session_view = CreateSession(self.create_session_ctrl, self.root)
        
        self.opening_screen_view.grid(row=0, column=0, sticky=ctk.NSEW)
        self.view_sessions_view.grid(row=0, column=0, sticky=ctk.NSEW)
        self.create_session_view.grid(row=0, column=0, sticky=ctk.NSEW)
        
        self.show_opening_screen()
        self.root.update_idletasks()
        self.root.deiconify() # Show the window after everything has finished loading
        self.root.update()
        
        self.root.mainloop()
        
    def get_current_monitor(self):
        """Gets the current active monitor. (for multi-monitor setups)"""
        self.root.update_idletasks()
        parts = self.root.wm_geometry().split("+")
        win_x, win_y = int(parts[1]), int(parts[2])
        
        for monitor in get_monitors():
            if (monitor.x <= win_x < monitor.x + monitor.width and
                monitor.y <= win_y < monitor.y + monitor.height):
                
                return monitor

        return None
    
    def apply_window_size(self):
        """Applies the window size based on the height_quo."""
        self.root.geometry(f"{round(self.current_window_width*self.height_quo)}x{round(self.current_window_height*self.height_quo)}")
        ctk.set_widget_scaling(self.height_quo)
        self.root.update()   
        
    def resize_window(self, window, current_monitor):
        """Periodically checks if the active monitor has changed and resizes if it has."""
        last_monitor = current_monitor
        
        new_monitor = self.get_current_monitor()
        
        if new_monitor is not None:
            current_monitor = new_monitor
                
        if (current_monitor != last_monitor):
            self.height_quo = current_monitor.height / 1200
            
            self.apply_window_size()
        
        self.root.after(100, self.resize_window, window, current_monitor)                
          
    @staticmethod
    def force_coordinate_update(widget):
        """Forces each widget to repaint itself. (solves visual bugs)"""
        for child in widget.winfo_children():
            if hasattr(child, "_draw"):
                child._draw()

            child.update() 
            
            if child.winfo_children():
                MainController.force_coordinate_update(child)   

    def show_opening_screen(self):
        """Brings the opening screen to the top."""
        self.opening_screen_view.tkraise()

    def show_sessions_screen(self):          
        """Brings the sessions view screen to the top."""
        self.view_sessions_view.tkraise()     
            
    def show_new_session_screen(self): 
        """Brings the new session screen to the top."""
        self.create_session_view.tkraise()
        
    def add_session_ctrl(self, new_ctrl):
        """Adds a session tab controller to the corresponding list."""
        if new_ctrl not in self.session_ctrls:
            self.session_ctrls.append(new_ctrl)
            
    def remove_session_ctrl(self, ctrl):
        """Removes a session tab controller from the corresponding list."""
        self.session_ctrls.remove(ctrl)
        
    def add_session(self, new_session_view):
        """Removes a session tab view to the corresponding list."""
        if new_session_view not in self.session_views:
            self.session_views.append(new_session_view)
        
    def remove_session(self, session_view):
        """Removes a session tab view from the corresponding list."""
        self.session_views.remove(session_view)
        
    def add_session_info(self, session_info):
        """
        Adds a session info dict to the corresponding lists if a dict with 
        the same name, user and server is not already present.
        """
        existing_keys_all = {
            (s["name"], s["user"], s["server"]) for s in self.all_sessions_info
        }
        existing_keys_synced = {
            (s["name"], s["user"], s["server"]) for s in self.synced_sessions_info
        }

        key = (
            session_info["name"],
            session_info["user"],
            session_info["server"],
        )

        if key not in existing_keys_all:
            self.all_sessions_info.append(session_info)
        if key not in existing_keys_synced:
            self.synced_sessions_info.append(session_info)
            
        self.sort_sessions_info()
            
    def sort_sessions_info(self):
        """
        Sorts the sessions_info by these parameters in this order:
        1. Whether the user and server attributes match the ones that were 
        used for the login
        2. The sting 'username@hostname'
        3. The name of the session (see _natural_sort_key for the details)
        """
        self.all_sessions_info.sort(
            key=lambda info: (
                info["user"] != self.user or info["server"] != self.server,
                f"{info["user"]}@{info["server"]}",
                self._natural_sort_key(info["name"]),
            )
        )
        self.synced_sessions_info.sort(
            key=lambda info: self._natural_sort_key(info["name"])
        )

    @staticmethod
    def _natural_sort_key(value):
        """
        Returns tuple of (type, value) pairs produced by splitting the string
        into numeric and non-numeric segments. Each numeric segment is
        converted to an integer and paired with a leading 1, while each
        non-numeric segment is kept as a casefolded string and paired with a
        leading 0. This lets Python sort strings in a natural way where
        digits are ordered numerically and text is ordered alphabetically.
        
        For example, 'session2' will be sorted lower than 'session10' and
        'session' lower than 'session1'.
        """
        return tuple(
            (1, int(part)) if part.isdigit() else (0, part.casefold())
            for part in re.split(r"(\d+)", value)
        )
            
    def remove_session_info(self, session_name):
        """
        Removes a set of session_infos specified by the name from the 
        synced and all lists.
        """
        self.synced_sessions_info = [
            session_info
            for session_info in self.synced_sessions_info
            if session_info["name"] != session_name
        ]
        self.all_sessions_info = [
            session_info
            for session_info in self.all_sessions_info
            if session_info["name"] != session_name or session_info["server"] != self.server or session_info["user"] != self.user
        ]
            
    def update_sessions_on_login(self):
        """
        Checks the logs on the server and updates the session's progress
        accordingly.
        """
        
        '''
        Check if any saved sessions belong to the username and hostname the
        user used to log in
        '''
        current_sessions = [
            (session, controller)
            for session, controller in zip(self.session_views, self.session_ctrls)
            if controller.server == self.server and controller.user == self.user
        ]
        if not current_sessions:
            return

        session_names = " ".join(
            shlex.quote(controller.session_name)
            for _, controller in current_sessions
        )
        # Get the names of all the sessions that have running logs present
        command = (
            f"for session_name in {session_names}; do "
            'if [ -f "$HOME/LLMPipe/$session_name.log" ]; then '
            'printf "%s\\n" "$session_name"; '
            "fi; done"
        )
        running_logs, err, error_code = self.ssh_controller.execute_command(command)
        if error_code != 0:
            print(err)
            ErrorPopup(self.root, err)
            return

        running_session_names = set(running_logs.splitlines())
        for session, controller in current_sessions:
            session.on_login_config()

            # Catch the logs of the running sessions
            if controller.session_name in running_session_names:
                _, stdout, _ = self.ssh_controller.ssh_client.exec_command(
                    f"tail -f ~/LLMPipe/{shlex.quote(controller.session_name)}.log"
                )
                controller.resume_progress_updates(
                    session, stdout, controller.sequence_progress
                )
            # Set the progress to 100% if no logs were present
            else:
                controller.progress = 1
                controller.sequence_progress = controller.sequence_count
                controller.finished = True
                session.update_finished_progress()
                    
    def save_sessions(self):
        """Save current progress info to json file."""
        if not self.server or not self.user:
            return

        session_map = {
            (controller.server, controller.user, controller.session_name): controller
            for controller in self.session_ctrls
        }

        for session_info in self.synced_sessions_info:
            session = session_map.get(
                (self.server, self.user, session_info["name"])
            )
            if session is not None:
                session_info["sequence_progress"] = session.sequence_progress
                session_info["progress"] = session.progress

        json_controller.save_sessions_info(
            hostname=self.server,
            username=self.user,
            sessions_info=self.synced_sessions_info
        )
       
    def sync_sessions(self):
        """Syncs local sessions info with actual state on the server."""
        tmux_sessions = self.ssh_controller.get_tmux_sessions()
        new_synced_sessions_info = (
            self._get_finished_sessions(tmux_sessions)
            + self._get_remote_sessions(tmux_sessions)
        )
        
        for session_info in new_synced_sessions_info:
           self.add_session_info(session_info)
        
        self.sort_sessions_info()
        
        # Remove sessions that are not present on the server
        for view, controller in list(zip(self.session_views, self.session_ctrls)):
            if (
                controller.session_name not in [info["name"] for info in self.synced_sessions_info]
                and controller.server == self.server
                and controller.user == self.user
            ):
                view.after_idle(view.delete_self)
                self.remove_session(view)
                self.remove_session_ctrl(controller)
        
    def _get_finished_sessions(self, tmux_sessions):
        """Get all finsished sessions info that are saved on the server."""
        # Get finished sessions paths
        paths = self.ssh_controller.get_finished_remote_paths()  
        running_sessions = set(tmux_sessions)
        
        # Group files by their parent directory (session name)
        dir_files = defaultdict(set)
        for filepath in paths.splitlines():
            p = Path(filepath)
            # Filter out partially finished sessions to avoid duplicates
            if p.parent.name not in running_sessions:
                dir_files[p.parent.name].add(p.name)
            
        session_dicts = []
        for session_name, files in dir_files.items():
            # Validate expected file contents
            has_scores = f"{session_name}_scores_table0.csv" in files
            has_file_ids = "fileIDs.txt" in files
            
            # There should be a csv file per sequence (minus 1 because of fileIDs.txt)
            if not has_scores or not has_file_ids:
                continue
                
            sequence_count = len(files) - 1
            session_dicts.append(
                {
                    "server": self.server,
                    "user": self.user,
                    "name": session_name,
                    "sequence_count": sequence_count,
                    "sequence_progress": sequence_count,
                    "progress": 1, 
                    "finished": True
                }
            )   
            
        return session_dicts
    
    def _get_remote_sessions(self, tmux_sessions):
        """Get all the sessions currently running on the server."""
        # Get running sessions info
        raw_output = self.ssh_controller.get_running_remote_sessions_info(tmux_sessions)
        session_dicts = []
        
        for line in raw_output.splitlines():
            if not line.strip():
                continue
            
            # Parse the structured "|"-delimited result
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            
            session_name, sequence_count, sequence_progress, last_log = parts[0], parts[1], parts[2], parts[3]
        
            match = re.search(r"Processing windows:\s*(\d+)%", last_log)
            progress = int(match.group(1)) if match else 0

            session_dicts.append(
                {
                    "server": self.server,
                    "user": self.user,
                    "name": session_name,
                    "sequence_count": int(sequence_count or 1),
                    "sequence_progress": int(sequence_progress) + 1 or 1,
                    "progress": progress/100,
                    "finished": False
                }
            )   
        
        return session_dicts
                    
    def on_closing(self):
        """Cleanup for when the program closes."""
        self.save_sessions()
        self.ssh_controller.close_clients()
        self.root.destroy()
        
        try:
            self.root.withdraw()
        except Exception:
            pass
                
        for after_id in self.root.tk.eval('after info').split():
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass
                
        try:
            self.root.quit()
        except Exception:
            pass 
        
        try:
            self.root.destroy()  
        except Exception:
            pass