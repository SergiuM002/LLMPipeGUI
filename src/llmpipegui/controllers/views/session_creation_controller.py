import os
import re
import threading

class CreateSessionController:
    """Coordinates the session creation screen."""
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        
        self.file_path = None
        self.selected_labels = []
        self.search_debounce_id = None 
        self.worker_thread = None
        self.search_countrer = 0
        
    # Imports file according to its header
    def import_file(self, view):
        """Checks the file extention and shows either import success or failure."""
        if self.file_path and any(x == self.file_path.split(".")[-1].lower() for x in ["fa", "fasta", "fna"]):
            view.show_general_import()
        else:
            view.show_import_failure() 
        
    def start_process(self, view):
        """Starts the session creation process."""
        msg = ""
        
        if not view.output_text.get():
            msg = "Please enter an output name."
        elif view.import_text.get() == "uploaded file: " or "(invalid file)" in view.import_text.get():
            msg = "Please upload a valid file."
        elif view.login_text.get() == "not logged in ✕":
            msg = "Please log in."
            
        if msg != "":
            view.show_start_error(msg) 
            return
        
        view.show_syncing_start()
        # Refresh the sessions so it can check if a session exists against the current state
        self.main_ctrl.view_sessions_ctrl.refresh_sessions()
        
        if self.session_exists(view.output_text.get()):
            view.show_session_exists_error()
            return
        
        self.fasta_file_name = view.output_text.get() + ".fa"
            
        view.show_filtering_start()
        self.filter_fasta(view)
        
        view.show_creating_session_start()
        self.start_session(view)
        view.show_creating_session_finish()
    
    def filter_fasta(self, view):
        """Filter the sequences based on the filter terms selected."""
        with open(self.file_path, "r") as file:
            file_content = file.read()
        
        output_string = ""
        output_lines = []
        keep = False
        
        selected_filters = []
        
        for label in self.selected_labels:
            selected_filters.append(label.cget("text"))
        
        if selected_filters:
            # Keep each FASTA header and sequence lines when its header matches a selected filter.
            for line in file_content.split("\n"):
                if line and line[0] == ">":
                    keep = False
                    for filter in selected_filters:
                        if filter in line:
                            keep = True
                if line and keep:
                    output_lines.append(line)
            output_string = "\n".join(output_lines)
        else:
            # With no filters selected, preserve the complete input file.
            output_string = file_content
        
        # Write the filtered data to a temporary local FASTA file for upload.
        with open(self.fasta_file_name, "w") as file:
            file.write(output_string)
        try:
            # Find the remote home directory and upload the FASTA into the LLMPipe folder.
            out, err, exit_code = self.main_ctrl.ssh_controller.execute_command("pwd")
            
            if exit_code != 0:
                print(err)
                view.show_error_popup(err)
                return
            
            home_dir = out.strip()
            
            try:
                self.main_ctrl.ssh_controller.upload_file(self.fasta_file_name, f"{home_dir}/LLMPipe/{self.fasta_file_name}")
            except RuntimeError as e:
                print(e)
                view.show_error_popup(str(e)) 
                return
                
        finally:
            # Always remove the temporary local copy, including when upload fails.
            os.remove(self.fasta_file_name)
        
    def start_session(self, view):
        """Starts a session."""
        out, err, exit_code = self.main_ctrl.ssh_controller.execute_command("pwd")
                    
        if exit_code != 0:
            print(err)
            view.show_error_popup(err)
            return
        
        home_dir = out.strip()
        
        # Get the sequence count by counting the number of lines starting with ">"
        sequence_count = 0
        for line in self.main_ctrl.ssh_controller.open_line_by_line(f"{home_dir}/LLMPipe/{view.output_text.get()}.fa"):
            if line.startswith(">"):
                sequence_count += 1

        # Add new session tab
        self.main_ctrl.view_sessions_ctrl.add_session(
            session_name=view.output_text.get(), 
            align=view.align_state.get(), 
            model_selection=view.model_selection.get(), 
            window_size_selection=view.window_size_selection.get(), 
            sequence_count=sequence_count
        )
            
    def session_exists(self, session_name):
        """Checks if a session with the specified name already exists."""
        check_cmd = f"tmux has-session -t ={session_name} 2>/dev/null"
        _, _, exit_code = self.main_ctrl.ssh_controller.execute_command(check_cmd)
        
        if exit_code == 0:
            return True
        
        for session in self.main_ctrl.session_ctrls:
            if session.session_name == session_name:
                return True
            
        return False
    
    def get_search_hits(self, view, search_selection_list):
        """Gets the search hits for the typed search."""
        
        # Cancels the previous timer if this function was triggered twice within 300ms
        if self.search_debounce_id:
            self.main_ctrl.root.after_cancel(self.search_debounce_id)
        
        search_term = view.filter_entry.get().strip().upper()
        if not search_term:
            view.display_search_results(search_selection_list, [])
            return
        
        # Saves a search ID it can keep track of whether this is the latest search
        self.search_countrer += 1
        current_search_id = self.search_countrer
              
        # Start searching after 300ms if the user does not keep typing
        self.search_debounce_id = self.main_ctrl.root.after(
            300, lambda: self._start_search_thread(view, search_term, search_selection_list, current_search_id)
        )
        
    def _start_search_thread(self, view, search_term, search_selection_list, search_id):
        """Starts the search thread."""
        worker_thread = threading.Thread(target=self.search_file, args=(view, search_term, search_selection_list, search_id), daemon=True)
        worker_thread.start()
    
    def search_file(self, view, search_term, search_selection_list, search_id):
        """Searches the imported file for the specified search term."""
        search_hits = set()
        
        delimiter_pattern = re.compile(r'[ |]+')
        
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    # Check if the user kept typing and a new search has started
                    if search_id != self.search_countrer:
                        return
                    
                    if ">" in line:
                        parts = line.split(">")
                        if len(parts) > 1:
                            content = parts[1].strip()
                            header_elements_orig = delimiter_pattern.split(content)
                            header_elements = delimiter_pattern.split(content.upper())
                            
                            
                            for element, orig_element in zip(header_elements, header_elements_orig):
                                if search_term in element:
                                    search_hits.add(orig_element) 
                                    
            # Another check for a new search before updating the GUI
            if search_id != self.search_countrer:
                return
            
            # Display the results so they can be selected
            self.main_ctrl.root.after(0, lambda: view.display_search_results(search_selection_list, list(search_hits)))
                    
        except Exception as e:
            print(f"Error searching file: {e}")
            
    def set_context_size_options(self, view):
        """Set the context size options based on the language model selected."""
        match view.model_selection.get():
            case "PlantCaduceus1":
                view.window_size_listbox.configure(values=view.window_size_options_pc1)
            case _:
                view.window_size_listbox.configure(values=view.window_size_options_pc2)   


    