import subprocess
import config.environment as env
import threading

class SessionTabController:
    def __init__(
        self, main_ctrl,         
        session_name, 
        sequence_count, 
        server,
        user,
        align=None, 
        model_selection=None, 
        window_size_selection=None, 
        progress=None, 
        sequence_progress=None, 
    ):
        
        self.main_ctrl = main_ctrl
        self.session_name = session_name
        self.align = align
        self.model_selection = model_selection
        self.window_size_selection = window_size_selection
        self.sequence_count = sequence_count
        self.progress = progress
        self.sequence_progress = sequence_progress
        self.server = server
        self.user = user
        
    def set_session_state(self, view):
        if self.model_selection != None and self.align != None:
            # When starting a fresh session
            self.progress = 0
            view.show_session_state_start()
            self.start_session(view)
        else:
            # When loading a session
            if self.progress == 1:
                if self.sequence_progress == self.sequence_count:
                    view.show_session_state_finished()
                else:
                    view.show_session_sequence_finished(self.sequence_progress, self.sequence_count)
            else:
                view.show_session_state_in_progress(self.sequence_progress, self.sequence_count, self.progress)
                
    def start_session(self, view):
        self.main_ctrl.ssh_controller.execute_command(f"touch ~/LLMPipe/{self.session_name}.log")
            
        command = (
            "cd ~/LLMPipe && "
            "source ../miniconda3/etc/profile.d/conda.sh && "
            "conda activate plantcad_env && "
            "python llm_pipe.py -f "
        )
        
        if self.align:
            command += "-m "
            
        if self.model_selection == "Caduceus":
            command += "-c "
        elif self.model_selection == "PlantCaduceus1":
            command += "-p1 "     
        elif self.model_selection == "PlantCaduceus2-Small":
            command += "-p2s "
        elif self.model_selection == "PlantCaduceus2-Medium":
            command += "-p2m "
        elif self.model_selection == "PlantCaduceus2-Large":
            command += "-p2l "
            
        if self.window_size_selection == "512bp":
            command += "-w 512 "
        elif self.window_size_selection == "1024bp":
            command += "-w 1024 "
        elif self.window_size_selection == "2048bp":
            command += "-w 2048 "
        elif self.window_size_selection == "4096bp":
            command += "-w 4096 "
        elif self.window_size_selection == "8192bp":
            command += "-w 8192 "

        command += (
            f"{self.session_name}.fa > {self.session_name}.log 2>&1 && " 
            f"rm ~/LLMPipe/{self.session_name}.fa && "
            f"rm ~/LLMPipe/{self.session_name}.log && "
            f"tmux kill-session -t {self.session_name}"
        )
        
        self.main_ctrl.ssh_controller.execute_command(f"tmux new-session -d -s {self.session_name}")

        self.main_ctrl.ssh_controller.execute_command(f'tmux send-keys -t {self.session_name} "{command}" C-m')

        _, stdout, _ = self.main_ctrl.ssh_controller.ssh_client.exec_command(f"tail -f ~/LLMPipe/{self.session_name}.log")   
        
        self.start_progress_updates(view, stdout)
        
    def start_progress_updates(self, view, stdout):
        self.sequence_progress = 1
        self.stop_event = threading.Event()
        self.stop_event.clear()
        self.worker_thread = threading.Thread(target=self.update_progress, args=(view, stdout, self.sequence_progress, True))
        self.worker_thread.start()
        
    def resume_progress_updates(self, view, stdout, sequence_progress):
        self.sequence_progress = sequence_progress
        self.stop_event = threading.Event()
        self.stop_event.clear()
        self.worker_thread = threading.Thread(target=self.update_progress, args=(view, stdout, self.sequence_progress, False))
        self.worker_thread.start()
        
    # Update the progress of the LLM
    def update_progress(self, view, stdout, sequence_progress, bar_packed=False):
        buffer = ""
        
        while not self.stop_event.is_set():
            self.stop_event.wait(timeout=0.5)
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(1048576).decode('utf-8', errors='ignore')
                buffer += chunk
                
                if '\n' in buffer:
                    if self.sequence_count > sequence_progress and "Processing windows: " in buffer:
                        sequence_progress += 1
                        self.sequence_progress = sequence_progress

                if '\r' in buffer and view.progress_text.get() != "transfering files...":
                    updates = buffer.split('\r')
                    current_status = updates[-1].strip()
                    
                    if "Processing windows: " in current_status:
                        percentage = current_status.split("Processing windows: ")[-1][0:4]
                        if "%" in percentage:   
                            if bar_packed == False:
                                bar_packed = True
                                self.main_ctrl.root.after(0, view.pack_progress_bar)
                            
                            self.progress = int(percentage[0:-1])/100
                            self.main_ctrl.root.after(0, view.update_percentage_progress, self.sequence_progress, self.sequence_count, percentage, self.progress)
                        else:
                            bar_packed = False
                            self.progress = 1
                            self.main_ctrl.root.after(0, view.update_processing_progress, self.sequence_progress, self.sequence_count)
                    
                    buffer = updates[-1]
                    
            if "Script finished." in buffer:
                self.stop_event.set()
                self.main_ctrl.root.after(0, view.update_finished_progress)
                stdout.channel.close()
                
    def get_files(self, output_path):
        _, _, exit_status = self.main_ctrl.ssh_controller.execute_command(
            f"tar -czf ~/LLMPipe/result.tar.gz -C ~/LLMPipe/results/{self.session_name} ."
        )
        
        if exit_status == 0:
            out, _, _ = self.main_ctrl.ssh_controller.execute_command("pwd")
            home_dir = out.strip()
            self.main_ctrl.ssh_controller.retrieve_file(f"{home_dir}/LLMPipe/result.tar.gz", f"{output_path}/{self.session_name}_results.tar.gz")
            self.main_ctrl.ssh_controller.execute_command("rm ~/LLMPipe/result.tar.gz")
        
        command = (
            f"cd '{output_path}' && "
            f"mkdir {self.session_name}_results && "
            f"tar -xf {self.session_name}_results.tar.gz -C {self.session_name}_results && "
        )
        
        if env.OPERATING_SYSTEM == "Windows":
            command += f"del {self.session_name}_results.tar.gz"
        else:
            command += f"rm {self.session_name}_results.tar.gz"
        
        subprocess.run(command, shell=True)
        
    def confirm_delete(self, view):
        finished = False
        
        if self.progress == 1 and self.sequence_count == self.sequence_progress:
            msg = "Are you sure?\nFiles not downloaded will be lost."
            finished = True
        else:
            msg = "Are you sure?\nThis will terminate the running session."
            
        if view.get_delete_confirmation(msg) == "Yes":
            self.delete_session(view, finished)
            
            
    def delete_session(self, view, finished):
        if finished:
            self.main_ctrl.ssh_controller.execute_command(f"rm -r ~/LLMPipe/results/{self.session_name}")  
        else:
            check_cmd = f"tmux has-session -t {self.session_name} 2>/dev/null"
            _, _, exit_status = self.main_ctrl.ssh_controller.execute_command(check_cmd)
        
            if exit_status == 0:
                self.main_ctrl.ssh_controller.execute_command(f"tmux kill-session -t {self.session_name}")
                
            _, _, exit_status = self.main_ctrl.ssh_controller.execute_command(f"[ -f ~/LLMPipe/{self.session_name}.log ]")
            
            if exit_status == 0:
                self.main_ctrl.ssh_controller.execute_command(f"rm ~/LLMPipe/{self.session_name}.log")
            
            _, _, exit_status = self.main_ctrl.ssh_controller.execute_command(f"[ -f ~/LLMPipe/{self.session_name}.fa ]")
            
            if exit_status == 0:
                self.main_ctrl.ssh_controller.execute_command(f"rm ~/LLMPipe/{self.session_name}.fa")
        
        self.main_ctrl.force_coordinate_update(view.master)
        self.cleanup(view)        
        view.delete_self()
        
    def cleanup(self, view):
        self.main_ctrl.remove_session_ctrl(self)
        self.main_ctrl.remove_session(view)
        self.main_ctrl.remove_session_info(self.session_name)
        
        self.view = None
        self.main_ctrl = None

            