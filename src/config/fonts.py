import customtkinter as ctk

class Fonts:
    def __init__(self, size_quo):
        self.roboto_fonts = {}
        
        for i in range(1, 30):
            self.roboto_fonts[i] = ctk.CTkFont(family="Roboto", size=round(i*size_quo))
        
        

    def resize_text(self, size_quo):
        for i in range(1, 30):
            self.roboto_fonts[i].configure(size=round(i*size_quo))
