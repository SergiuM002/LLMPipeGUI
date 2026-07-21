class OpeningScreenController:
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        
    def show_projects_screen(self):
        self.main_ctrl.show_projects_screen()
        
    def show_new_project_screen(self):
        self.main_ctrl.show_new_project_screen()
        