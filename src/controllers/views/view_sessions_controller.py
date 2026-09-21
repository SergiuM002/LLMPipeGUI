from ui.components.session_tab import SessionTab
from ui.views.login_window import LoginWindow
from controllers.components.session_tab_controller import SessionTabController
from controllers.views.login_window_controller import LoginWindowController

class ViewSessionsController:
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        self.view = None
        
    def connect_view(self, view):
        self.view = view    
    
    def load_sessions(self):
        self.main_ctrl.load_sessions_info()
        new_sessions = []
        
        for session_info in self.main_ctrl.sessions_info:
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
        
        for new_session in new_sessions:
            self.view.show_session(new_session)
            
    def reload_sessions(self):
        for session_view in self.main_ctrl.sessions:
            session_view.after_idle(session_view.delete_self)

        self.main_ctrl.sessions = []
        self.main_ctrl.session_ctrls = []
    
        self.load_sessions()
        
    def refresh_sessions(self):
        self.main_ctrl.sync_sessions()
        self.main_ctrl.update_sessions_on_login()
            
    def add_session(self, session_name, align, model_selection, window_size_selection, sequence_count):
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
        })
        self.view.show_session(new_session)
            
    def show_login_window(self, view):
        LoginWindow(LoginWindowController(self.main_ctrl), view)
        
    def update_sessions_on_login(self):
        self.main_ctrl.update_sessions_on_login()

