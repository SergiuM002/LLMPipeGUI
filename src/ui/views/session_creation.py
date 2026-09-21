import subprocess
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from ui.error_popup import ErrorPopup
from customtkinter import filedialog
from ui.components.collapsible_multiselect import CollapsibleMultiSelect
from controllers.components.collapsible_multiselect_controller import CollapsibleMultiselectController
from ui.views.login_window import LoginWindow
from controllers.views.login_window_controller import LoginWindowController
from config.styles import Theme
import config.environment as env

class CreateSession(ctk.CTkFrame):
    def __init__(self, controller, master, **kwargs):   
        super().__init__(master, fg_color="transparent", **kwargs)
        self.master = master
        self.controller = controller
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)  
            
        self.button_frame1 = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent",
            width=0,
            height=0
        ) 
        
        self.button_frame1.pack(fill="x")
        
        self.back_button = ctk.CTkButton(
            self.button_frame1,
            text="Back",
            font=("Roboto", 18),
            command=self.back,
            width=100,
            height=40,
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
        )

        self.back_button.pack(side=ctk.LEFT, padx=(50, 20), pady=(20, 0))
        
        self.import_button = ctk.CTkButton(
            self.button_frame1, 
            text="Import FASTA",
            height=40,
            command=self.import_button_clicked,
            font=("Roboto", 19),
            fg_color=Theme.GREEN_BUTTON,
            text_color=Theme.GREEN_BUTTON_TEXT,
            hover_color=Theme.GREEN_BUTTON_HOVER,
        )
        self.import_button.pack(side=ctk.LEFT, fill="x", expand=True, padx=(0, 50), pady=(20, 0))

        self.import_text = ctk.StringVar(self.scroll_frame, "uploaded file: ")
        self.import_label = ctk.CTkLabel(self.scroll_frame, textvariable=self.import_text, font=("Roboto", 12), text_color=Theme.GENERAL_LABEL)
        self.import_label.pack(anchor=ctk.W, padx=50, pady=(5, 0))

        self.filter_frame1 = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", width=0, height=0)
        self.filter_frame1.pack(fill="x", padx=50)

        self.search_frame = ctk.CTkFrame(self.filter_frame1, fg_color="transparent", height=300, width=200)
        self.search_frame.pack_propagate(False)
        self.filter_label = ctk.CTkLabel(self.search_frame, text="Enter a filter term:", font=("Roboto", 13), text_color=Theme.GENERAL_LABEL)
        self.filter_entry = ctk.CTkEntry(self.search_frame, text_color=Theme.GENERAL_LABEL)
        self.filter_entry.bind("<KeyRelease>", lambda e: self.field_search(self.filter_list))
        self.filter_list = CollapsibleMultiSelect(
            CollapsibleMultiselectController(controller.main_ctrl, []), 
            self.search_frame, 
            "Search hits", 
            0.8, 
            1
        )
        self.selected_list = ctk.CTkScrollableFrame(self.filter_frame1)

        self.align_state = ctk.BooleanVar(value=True)
        self.align_checkbox = ctk.CTkCheckBox(
            self.scroll_frame, 
            text="align sequences",
            font=("Roboto", 16),
            checkbox_height=24,
            checkbox_width=24,
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            variable=self.align_state,
            border_color=("gray45", "gray55"),
            text_color=Theme.GENERAL_LABEL
        )

        self.align_checkbox.pack(anchor=ctk.W, padx=50, pady=25)

        self.output_label = ctk.CTkLabel(self.scroll_frame, text="Output name (without file extension):", font=("Roboto", 16), text_color=Theme.GENERAL_LABEL)
        self.output_label.pack(anchor=ctk.W, padx=50, pady=(0, 10))

        self.output_text = ctk.CTkEntry(self.scroll_frame, height=40, font=("Roboto", 18))
        self.output_text.pack(anchor=ctk.W, fill="x", padx=50, pady=(0, 15))
        
        self.button_frame2 = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.button_frame2.pack(fill="x", pady=(100, 0))

        self.login_button = ctk.CTkButton(
            self.button_frame2, 
            height=40, 
            text="login", 
            font=("Roboto", 18),
            fg_color=Theme.GRAY_BUTTON,
            text_color=Theme.GRAY_BUTTON_TEXT,
            hover_color=Theme.GRAY_BUTTON_HOVER,
            command=lambda: LoginWindow(LoginWindowController(self.controller.main_ctrl), self)
        )
        self.login_button.pack(side=ctk.LEFT, padx=(50, 15))

        self.login_text = ctk.StringVar(self.button_frame2, "not logged in ✕")
        self.login_label = ctk.CTkLabel(self.button_frame2, textvariable=self.login_text, font=("Roboto", 14), text_color=Theme.GENERAL_LABEL)
        self.login_label.pack(side=ctk.LEFT, padx = 0, pady=20)

        self.start_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.start_frame.pack(fill="x", padx=(50, 5), pady=(20, 0))

        self.start_button = ctk.CTkButton(
            self.start_frame, 
            height=40, 
            text="START", 
            font=("Roboto", 18), 
            text_color=("white"),
            fg_color=Theme.GREEN_BUTTON,
            hover_color=Theme.GREEN_BUTTON_HOVER,
            command=self.start_button_clicked
        )
        self.start_button.pack(side=ctk.LEFT, anchor=ctk.N)
        
        self.model_frame = ctk.CTkFrame(self.start_frame, fg_color="transparent")
        self.model_frame.pack(side=ctk.LEFT, padx=(20, 0))

        self.model_selection = ctk.StringVar(self.model_frame, "PlantCaduceus1")
        model_options = ["PlantCaduceus2-Small", "PlantCaduceus2-Medium", "PlantCaduceus2-Large", "PlantCaduceus1", "Caduceus"]
        self.model_listbox = ctk.CTkComboBox(
            self.model_frame, 
            height=30, 
            width=200,
            state="readonly", 
            variable=self.model_selection, 
            values=model_options,
            font=("Roboto", 13),
            text_color=Theme.GENERAL_LABEL
        )
        self.model_listbox.pack()
        
        self.window_size_selection = ctk.StringVar(self.model_frame, "512bp")
        window_size_options = ["512bp", "1024bp", "2048bp", "4096bp", "8192bp"]
        self.window_size_listbox = ctk.CTkComboBox(
            self.model_frame, 
            height=30, 
            width=90,
            state="readonly", 
            variable=self.window_size_selection, 
            values=window_size_options,
            font=("Roboto", 13),
            text_color=Theme.GENERAL_LABEL
        )
        self.window_size_listbox.pack(anchor=ctk.W, pady=(10, 0))

        self.progress_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x")

        self.progress_text = ctk.StringVar(self.progress_frame, "")
        self.progress_label = ctk.CTkLabel(self.progress_frame, textvariable=self.progress_text, font=("Roboto", 13), text_color=Theme.GENERAL_LABEL)
        self.progress_label.pack(side=ctk.LEFT, padx=(50, 10), pady=(15, 5))

    def import_button_clicked(self):
        chosen_path = ""
        
        if env.OPERATING_SYSTEM == "Linux":
            try:
                chosen_path = subprocess.check_output(
                    [
                        'zenity', 
                        '--file-selection', 
                        '--title=Select a FASTA file', 
                        '--file-filter=FASTA files | *.fa *.fasta *.fna'
                    ],
                    stderr=subprocess.STDOUT
                ).decode('utf-8').strip()
                chosen_path = chosen_path.splitlines()[-1]
            except subprocess.CalledProcessError:
                return None
        else:
            chosen_path = filedialog.askopenfilename(title="Select a file", filetypes=[("FASTA files", "*.fa *.fasta *.fna")])
        
        if chosen_path:
            self.controller.file_path = chosen_path
            
        self.controller.import_file(self)
        
    def start_button_clicked(self):
        self.controller.start_process(self)
        
    def show_syncing_start(self):
        self.progress_text.set("syncing...")
        self.progress_label.update()   
        
    def show_filtering_start(self):
        self.progress_text.set("filtering...")
        self.progress_label.update()
        
    def show_creating_session_start(self):
        self.progress_text.set("creating session...")
        self.progress_label.update()
        
    def show_creating_session_finish(self):
        self.progress_text.set("session created")
        self.progress_label.update()
        
    def show_session_exists_error(self):
        self.progress_text.set("Session already exists.")
        self.progress_label.update()
        
    def show_start_error(self, msg):
        scaling = self.controller.main_ctrl.height_quo
        ErrorPopup(self.controller.main_ctrl.root, scaling, msg)
        
    def show_import_failure(self):
        self.filter_entry.delete(0, ctk.END)
        for widget in self.filter_frame1.winfo_children():
            widget.pack_forget()
        self.filter_frame1.configure(height=1)
        self.search_frame.pack_forget()
        
        self.import_text.set("uploaded file: (invalid file)")
        
    def show_error_popup(self, message):
        ErrorPopup(self.controller.main_ctrl.root, self.controller.main_ctrl.height_quo, str(message))
                
    def show_general_import(self):    
        self.import_text.set("uploaded file: "+self.controller.file_path) 
        for widget in self.filter_frame1.winfo_children():
            widget.pack_forget()
            
        for label in self.controller.selected_labels:
            label.destroy()
        self.controller.selected_labels = []
        
        self.filter_entry.delete(0, ctk.END)
        self.field_search(self.filter_list)
            
        self.search_frame.pack(side=ctk.LEFT, anchor=ctk.NW, fill="y")
        self.selected_list.pack(side=ctk.RIGHT, anchor=ctk.NE, fill="both", pady=(15, 0), padx=(20, 0))
        self.filter_label.pack(anchor=ctk.W, pady=(15, 0))
        self.filter_entry.pack(anchor=ctk.W, pady=(5, 15))
        
        self.filter_list.pack(anchor=ctk.W, pady=(15, 0))
        
        self.controller.main_ctrl.force_coordinate_update(self.scroll_frame)
        
            
    # Update list of selected filters
    def select_filter(self, cb):
        if cb.get() == 1:
            new_label = ctk.CTkLabel(self.selected_list, text=cb.cget("text"))
            self.controller.selected_labels.append(new_label)
            new_label.pack()
        else:
            for label in self.controller.selected_labels[:]:
                if label.cget("text") == cb.cget("text"):
                    label.pack_forget()
                    label.destroy()
                    self.controller.selected_labels.remove(label)
        
    # Update filter options based on search
    def field_search(self, search_selection_list):       
        self.controller.get_search_hits(self, search_selection_list)
    
    def display_search_results(self, search_selection_list, search_hits):   
        if len(search_hits) > 50:
            search_selection_list.controller.load_new_options(list(search_hits)[:50], num_options=len(search_hits))  
        else:
            search_selection_list.controller.load_new_options(list(search_hits))
            
        for cb in self.filter_list.checkboxes:
            for label in self.controller.selected_labels:
                if label.cget("text") == cb.cget("text"):
                    cb.toggle()
        
            cb.configure(command=lambda current_cb=cb: self.select_filter(current_cb))
            
        self.filter_list.content_frame._parent_canvas.yview_moveto(0)

    # Update widgets after login
    def update_login(self):
        self.login_text.set("logged in ✓")
        self.login_label.update()
        self.login_button.configure(state="disabled")

    def back(self):
        scaling = self.controller.main_ctrl.height_quo
        msg = CTkMessagebox(
            master=self.controller.main_ctrl.root,
            title="Save changes?",
            message="Do you want to save changes?",
            icon="question",
            option_1="Cancel",
            option_2="No",
            option_3="Yes",
            width=int(400*scaling),
            height=int(200*scaling),
            button_width=int(130*scaling),
            button_height=int(40*scaling),
            button_color=(Theme.GREEN_BUTTON, Theme.GRAY_BUTTON, Theme.GRAY_BUTTON),
            button_hover_color=Theme.GRAY_BUTTON_HOVER
        )
        
        response = msg.get()
        
        if response == "Yes":
            self.controller.main_ctrl.show_opening_screen()
        elif response == "No":
            for widget in self.filter_frame1.winfo_children():
                widget.pack_forget()
            self.filter_frame1.configure(height=1)
            self.search_frame.pack_forget()
    
            self.import_text.set("uploaded file: ")
            self.align_state.set(True)
            self.model_selection.set("PlantCaduceus1")
            self.output_text.delete(0, ctk.END)
            self.progress_text.set("")
            
            self.controller.file_path = None
            self.controller.selected_labels.clear()
      
            self.controller.main_ctrl.show_opening_screen()