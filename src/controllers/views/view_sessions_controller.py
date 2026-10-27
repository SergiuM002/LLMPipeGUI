from ui.components.session_tab import SessionTab
from ui.views.login_window import LoginWindow
from controllers.components.session_tab_controller import SessionTabController
from controllers.views.login_window_controller import LoginWindowController
import controllers.json_controller as json_controller

class ViewSessionsController:
    """Coordinates session data and actions for the sessions screen."""

    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        self.view = None
        
    def connect_view(self, view):
        """Save a reference to the corresponding sessions view."""
        self.view = view    
    
    def load_sessions(self, only_synced=False):
        """
        Display sessions, creating tabs for sessions not already loaded.

        Set ``only_synced`` to display only sessions synchronized with the
        server. Otherwise, use the complete session list.
        """
        if only_synced:
            sessions_info = self.main_ctrl.synced_sessions_info
        else:
            sessions_info = self.main_ctrl.all_sessions_info
            
        new_sessions = []
        # Reuse existing tabs rather than creating duplicate views.
        session_view_map = {view.controller.session_name: view for view in self.main_ctrl.session_views}
        
        for session_info in sessions_info:
            if session_info["name"] in [ctrl.session_name for ctrl in self.main_ctrl.session_ctrls]:
                self.view.show_session(session_view_map[session_info["name"]])
                continue
            
            new_ctrl = SessionTabController(
                main_ctrl=self.main_ctrl,
                session_name=session_info["name"],
                sequence_count=session_info["sequence_count"],
                sequence_progress=session_info["sequence_progress"],
                progress=session_info["progress"],  
                server=session_info["server"],
                user=session_info["user"]
            )
            new_session = SessionTab(
                controller=new_ctrl,
                master=self.view.scroll_frame, 
            )
            new_sessions.append(new_session)
            
            self.main_ctrl.add_session_ctrl(new_ctrl)
            self.main_ctrl.add_session(new_session)
            
            self.view.show_session(new_session)
            
    def reload_sessions(self, only_synced=False):
        """Hide the current tabs and load the selected session list again."""
        for session_view in self.main_ctrl.session_views:
            session_view.pack_forget()
    
        self.load_sessions(only_synced=only_synced)
        
    def refresh_sessions(self):
        """Synchronize sessions, update the display and save the results."""
        self.view.refresh_button.configure(state="disabled")
        
        self.main_ctrl.sync_sessions()
        
        self.view.scroll_frame.pack_forget()
        self.reload_sessions(only_synced=self.view.only_synced_checkbox.get())
        self.view.scroll_frame.pack(fill="both", expand=True)
        
        self.main_ctrl.update_sessions_on_login()
        self.main_ctrl.save_sessions()
        
        self.view.refresh_button.configure(state="normal")
            
    def add_session(self, session_name, align, model_selection, window_size_selection, sequence_count):
        """Create a session tab, store its initial state, and refresh the list."""
        new_ctrl = SessionTabController(
            main_ctrl=self.main_ctrl, 
            session_name=session_name, 
            align=align,
            model_selection=model_selection,
            window_size_selection=window_size_selection,
            sequence_count=sequence_count,
            server=self.main_ctrl.server,
            user=self.main_ctrl.user
        )
        new_session = SessionTab(
            controller=new_ctrl, 
            master=self.view.scroll_frame
        )
        
        self.main_ctrl.add_session_ctrl(new_ctrl)
        self.main_ctrl.add_session(new_session)
    
        self.main_ctrl.add_session_info({
            "server": self.main_ctrl.server,
            "user": self.main_ctrl.user,
            "name": session_name,
            "sequence_count": sequence_count,
            "sequence_progress": 0,
            "progress": 0,
            "finished": False
        })
        self.refresh_sessions()
            
    def show_login_window(self, view):
        """Open a login window."""
        LoginWindow(LoginWindowController(self.main_ctrl), view)
        
    def toggle_only_synced(self):
        """Reload sessions according to the synced-only checkbox setting."""
        if self.view.only_synced_checkbox.get():
            canvas = self.view.scroll_frame._parent_canvas
            # Save the current scroll position before rebuilding the session list
            old_bounds = canvas.bbox("all")
            old_height = old_bounds[3] - old_bounds[1] if old_bounds else 0
            old_top = canvas.yview()[0] * old_height

            self.reload_sessions(only_synced=True)
            
            # Recalculate widget geometry so the new scrollable height is accurate
            self.view.scroll_frame.update_idletasks()

            # Calculate the new scroll max position
            new_bounds = canvas.bbox("all")
            if new_bounds:
                new_height = new_bounds[3] - new_bounds[1]
                max_top = max(0, new_height - canvas.winfo_height())
                # Keep the view within the new bounds if filtering shortened the list
                if old_top > max_top:
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    canvas.yview_moveto(1.0)
            
        else:
            self.reload_sessions(only_synced=False)
        
        
