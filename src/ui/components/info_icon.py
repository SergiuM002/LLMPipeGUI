import customtkinter as ctk

class InfoIcon(ctk.CTkLabel):
    def __init__(self, master, message, **kwargs):
        super().__init__(master, 
                         text="?", 
                         width=20, 
                         height=20, 
                         corner_radius=10,
                         fg_color="gray30", 
                         text_color="white",
                         font=("Arial", 12, "bold"),
                         **kwargs)
        
        self.message = message
        self.tooltip = None
        
        self.bind("<Enter>", self.show_tooltip)
        self.bind("<Leave>", self.hide_tooltip)
 

    def show_tooltip(self, event=None):
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + 25
        y += self.winfo_rooty() + 5

        self.tooltip = ctk.CTkToplevel(self)
        self.tooltip.wm_overrideredirect(True)  
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(self.tooltip, 
                             text=self.message, 
                             fg_color="#3d3d3d", 
                             padx=10, pady=5,
                             corner_radius=6)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None