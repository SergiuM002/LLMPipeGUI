class OpeningScreenController:
    """Coordinates the opening screen."""
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        
    def show_sessions_screen(self):
        """Brings the sessions screen to the top."""
        self.main_ctrl.show_sessions_screen()
        
    def show_new_session_screen(self):
        """Brings the session creation screen to the top."""
        self.main_ctrl.show_new_session_screen()
        