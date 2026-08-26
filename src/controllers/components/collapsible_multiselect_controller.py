import config.environment as env

class CollapsibleMultiselectController:
    def __init__(self, main_ctrl, options, options_info=None):
        self.main_ctrl = main_ctrl
        
        self.options = options
        self.options_info = options_info
        
        self.is_open = False
        self.view = None
        
    def connect_view(self, view):
        self.view = view
        
    def pack_options(self):
        try:
            if (len(self.options) == len(self.options_info)):
                has_infoboxes = True
            else:
                has_infoboxes = False
        except (TypeError):
            has_infoboxes = False
            
        for i in range(len(self.options)):
            if has_infoboxes:
                self.view.pack_option(has_infoboxes, self.options[i], self.options_info[i])
            else:
                self.view.pack_option(has_infoboxes, self.options[i], None)
            
        #self.apply_universal_bindings()
        self.main_ctrl.force_coordinate_update(self.view.winfo_toplevel())
            
    def toggle(self):
        if self.is_open:
            self.view.collapse_list()
        else:
            self.view.expand_list()
        self.is_open = not self.is_open
        
    def get_canvas(self):
        for attr in ['canvas', '_canvas', '_parent_canvas']:
            if hasattr(self.view.content_frame, attr):
                return getattr(self.view.content_frame, attr)
        return None

                
    def load_new_options(self, options, options_info=None, num_options=None):
        self.options = options
        self.options_info = options_info
        
        self.view.clean_old_options()
        
        if num_options:
            self.view.pack_remaining_label(num_options)
        self.pack_options()
        

        
        
            

            

            


            
        