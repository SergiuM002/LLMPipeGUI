from CTkMessagebox import CTkMessagebox
from config.styles import Theme

class ErrorPopup(CTkMessagebox):
    def __init__(self, master, scaling, message):        
        super().__init__(
            master=master, 
            title="Error", 
            message=message,
            icon="cancel",
            width=int(400*scaling),
            height=int(200*scaling),
            button_width=int(130*scaling),
            button_height=int(40*scaling),
            button_color=Theme.GREEN_BUTTON,
            button_hover_color=Theme.GREEN_BUTTON_HOVER
        )