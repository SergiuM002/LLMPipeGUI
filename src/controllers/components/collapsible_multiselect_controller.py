import config.environment as env

class CollapsibleMultiselectController:
    def __init__(self, main_ctrl, options, options_info=None):
        self.main_ctrl = main_ctrl
        
        self.options = options
        self.options_info = options_info
        
        self.is_open = False
        self.view = None
        
    def connect_view(self, view):
        """Saves a reference to the corresponding view."""
        self.view = view
        
    def pack_options(self):
        """Packs all the options."""
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
            
        self.main_ctrl.force_coordinate_update(self.view.winfo_toplevel())
            
    def toggle(self):
        """Expands or collapses the list."""
        if self.is_open:
            self.view.collapse_list()
        else:
            self.view.expand_list()
        self.is_open = not self.is_open
        
    def get_canvas(self):
        """Returns the canvas attribute of the view's content frame."""
        for attr in ['canvas', '_canvas', '_parent_canvas']:
            if hasattr(self.view.content_frame, attr):
                return getattr(self.view.content_frame, attr)
        return None

                
    def load_new_options(self, options, options_info=None, num_options=None):
        """Loads and packs the specified options."""
        self.options = options
        self.options_info = options_info
        
        self.view.clean_old_options()
        
        if num_options:
            self.view.pack_remaining_label(num_options)
        self.pack_options()
        

        
        
            

            

            


            
        