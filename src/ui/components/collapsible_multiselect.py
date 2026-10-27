import customtkinter as ctk
import platform
from ui.components.info_icon import InfoIcon
from config.styles import Theme

class CollapsibleMultiSelect(ctk.CTkFrame):
    """Display a collapsible list of checkbox options supplied by a controller."""

    def __init__(self, controller, master, title, checkbox_size, content_height, **kwargs):
        """
        Create the widget and populate it with the controller's options.

        ``checkbox_size`` scales checkbox dimensions and typography, while
        ``content_height`` scales the scrollable area's height.
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        self.os_type = platform.system()
        self.checkbox_size = checkbox_size
        self.controller = controller
        self.title = title
        self.rem_label = None
        
        self.controller.connect_view(self)
        
        # Match the arrow shown on the toggle button to the controller state
        if self.controller.is_open:
            self.toggle_button = ctk.CTkButton(
                self, text=f"▼ {title}", 
                command=self.controller.toggle,
                anchor="w",
                fg_color=("gray85", "gray25"),
                text_color=("gray20", "white"),
                hover_color=("gray80", "gray30"),
                font=("Roboto", 13)
            )
        else:
            self.toggle_button = ctk.CTkButton(
                self, text=f"▶ {title}", 
                command=self.controller.toggle,
                anchor="w",
                fg_color=("gray85", "gray25"),
                text_color=("gray20", "white"),
                hover_color=("gray80", "gray30"),
                font=("Roboto", 13)
            )
            
        self.toggle_button.pack(fill="x", expand=True)

        # Keep options in a scrollable area
        self.content_frame = ctk.CTkScrollableFrame(self, height=250*content_height)
        if (self.controller.is_open):
            self.content_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        # Let the controller create each option through ``pack_option``
        self.checkboxes = []
        self.option_frames = []
        self.controller.pack_options() 
        
    def pack_option(self, has_infoboxes, option, option_info):
        """Add one checkbox option, optionally accompanied by an info icon."""
        option_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        option_frame.pack(fill="x", anchor="w")
        
        cb = ctk.CTkCheckBox(
            option_frame, 
            text=option, 
            font=("Roboto", round(14*self.checkbox_size)),
            text_color=Theme.GENERAL_LABEL,
            border_color=("gray45", "gray55"),
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            checkbox_height=round(22*self.checkbox_size),
            checkbox_width=round(22*self.checkbox_size)
        )
        cb.pack(side=ctk.LEFT, pady=5*self.checkbox_size, padx=10, anchor="w")
        
        if has_infoboxes:
            InfoIcon(option_frame, message=option_info).pack(side=ctk.LEFT)
        
        self.checkboxes.append(cb)
        self.option_frames.append(option_frame)
        
    def pack_remaining_label(self, num_options):
        """Show a label indicating that only the first 50 options are displayed."""
        self.rem_label = ctk.CTkLabel(
            self.content_frame,
            text=f"(showing 50 of {num_options})",
            font=("Roboto", round(14*self.checkbox_size)),
            text_color=Theme.GENERAL_LABEL
        )
        self.rem_label.pack(pady=5, padx=10, anchor="w")
        
    def expand_list(self):
        """Show the scrollable options and indicate the expanded state."""
        self.content_frame.pack(fill="both", expand=True, pady=(5, 0))
        self.toggle_button.configure(text=f"▼ {self.toggle_button.cget('text')[2:]}")   
        
    def collapse_list(self):
        """Hide the scrollable options and indicate the collapsed state."""
        self.content_frame.pack_forget()
        self.toggle_button.configure(text=f"▶ {self.toggle_button.cget('text')[2:]}")
    
    def clean_old_options(self):
        """Destroy existing option widgets and reset their tracked references."""
        for checkbox in self.checkboxes:
            checkbox.destroy()
        for option in self.option_frames:
            option.destroy()
        if self.rem_label:
            self.rem_label.destroy()
            self.rem_label = None
            
        self.checkboxes = []
        self.option_frames = []
                

                