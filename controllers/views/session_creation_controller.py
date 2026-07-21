import config.environment as env
import os
import re
import threading

class CreateSessionController:
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        
        self.file_path = None
        self.selected_labels = []
        self.search_debounce_id = None 
        self.worker_thread = None
        self.search_countrer = 0
        
    # Imports file according to its header
    def import_file(self, view):
        if self.file_path and any(x == self.file_path.split(".")[-1].lower() for x in ["fa", "fasta", "fna"]):
            view.show_general_import()
        else:
            view.show_import_failure() 
        
    def start_process(self, view):
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
        
        if self.session_exists(view.output_text.get()):
            view.show_session_exists_error()
            return
        
        self.final_file = view.output_text.get() + ".fa"
            
        view.show_filtering_start()
        self.filter_fasta()
        
        view.show_creating_session_start()
        self.start_session(view)
        view.show_creating_session_finish()
    
    def filter_fasta(self):
        with open(self.file_path, "r") as file:
            file_content = file.read()
        
        output_string = ""
        output_lines = []
        keep = False
        
        # filter logic
        selected_filters = []
        
        for label in self.selected_labels:
            selected_filters.append(label.cget("text"))
        
        if selected_filters:
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
            output_string = file_content
        
        with open(self.final_file, "w") as file:
            file.write(output_string)
        try:
            out, _, _ = self.main_ctrl.ssh_controller.execute_command("pwd")
            home_dir = out.strip()
            self.main_ctrl.ssh_controller.transfer_file(self.final_file, f"{home_dir}/LLMPipe/{self.final_file}")
        finally:
            os.remove(self.final_file)
        
    def start_session(self, view):
        with open(self.file_path, "r") as file:
            sequence_count = sum(1 for line in file if line.startswith(">"))
        
        self.main_ctrl.view_sessions_ctrl.add_session(
            session_name=view.output_text.get(), 
            align=view.align_state.get(), 
            model_selection=view.model_selection.get(), 
            window_size_selection=view.window_size_selection.get(), 
            sequence_count=sequence_count
        )
            
    # Checks if a session with the specified name already exists
    def session_exists(self, session_name):
        check_cmd = f"tmux has-session -t {session_name} 2>/dev/null"
        _, _, exit_code = self.main_ctrl.ssh_controller.execute_command(check_cmd)
        
        if exit_code == 0:
            return True
        
        for session in self.main_ctrl.session_ctrls:
            if session.session_name == session_name:
                return True
            
        return False
    
    # Gets the search hits for the typed search
    def get_search_hits(self, view, search_selection_list):
        if self.search_debounce_id:
            self.main_ctrl.root.after_cancel(self.search_debounce_id)
        
        search_term = view.filter_entry.get().strip().upper()
        if not search_term:
            view.display_search_results(search_selection_list, [])
            return
        
        self.search_countrer += 1
        current_search_id = self.search_countrer
              
        self.search_debounce_id = self.main_ctrl.root.after(
            300, lambda: self._start_search_thread(view, search_term, search_selection_list, current_search_id)
        )
        
    def _start_search_thread(self, view, search_term, search_selection_list, search_id):
        worker_thread = threading.Thread(target=self.search_file, args=(view, search_term, search_selection_list, search_id), daemon=True)
        worker_thread.start()
    
    def search_file(self, view, search_term, search_selection_list, search_id):
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
                            header_elements = delimiter_pattern.split(content.upper())
                            
                            for element in header_elements:
                                if search_term in element:
                                    search_hits.add(element) 
                                    
            # Another check for a new search before updating the GUI
            if search_id != self.search_countrer:
                return
            
            self.main_ctrl.root.after(0, lambda: view.display_search_results(search_selection_list, list(search_hits)))
                    
        except Exception as e:
            print(f"Error searching file: {e}")
                                
            
        
        
    