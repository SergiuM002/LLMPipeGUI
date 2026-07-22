import json
import customtkinter as ctk
from tkinter import font as tkfont
from screeninfo import get_monitors
from ui.views.session_creation import CreateSession 
from ui.views.opening_screen import OpeningScreen
from ui.views.view_sessions import ViewSessions
from controllers.views.session_creation_controller import CreateSessionController 
from controllers.views.opening_screen_controller import OpeningScreenController 
from controllers.views.view_sessions_controller import ViewSessionsController 
from controllers.ssh_controller import SSHController
import config.environment as env
from config.fonts import Fonts
from pathlib import Path

class MainController:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.title("LLMPipeScoreVisualizer")
        self.root.resizable(False, False)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        
        self.current_monitor = get_monitors()[0]

        for m in get_monitors():
            if m.is_primary:
                self.current_monitor = m
                
        self.ssh_controller = SSHController(self)
        self.logged_in = False
        self.server = ""
        self.user = ""
        self.height_quo = self.current_monitor.height/1200
        self.fonts = Fonts(self.height_quo)

        self.original_window_height = 545
        self.original_window_width = 545
        
        self.current_window_height = self.original_window_height
        self.current_window_width = self.original_window_width

        self.root.wm_geometry("")

        self.root.geometry(f"{round(self.original_window_width*self.height_quo)}x{round(self.original_window_height*self.height_quo)}")

        self.views = {}
        
        self.session_ctrls = []
        self.sessions = []
        self.sessions_info = []
        
        self.root.after(200, self.resize_window, self.root, self.current_monitor)
        
        self.opening_screen_ctrl = OpeningScreenController(self)
        self.opening_screen_view = OpeningScreen(self.opening_screen_ctrl, self.root)
        
        self.view_sessions_ctrl = ViewSessionsController(self)
        self.view_sessions_view = ViewSessions(self.view_sessions_ctrl, self.root)
        
        self.create_session_ctrl = CreateSessionController(self)
        self.create_session_view = CreateSession(self.create_session_ctrl, self.root)
        
        self.opening_screen_view.grid(row=0, column=0, sticky=ctk.NSEW)
        self.view_sessions_view.grid(row=0, column=0, sticky=ctk.NSEW)
        self.create_session_view.grid(row=0, column=0, sticky=ctk.NSEW)
        
        self.show_opening_screen()
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.update()
        
        self.root.mainloop()
        
    def get_current_monitor(self):
        self.root.update_idletasks()
        parts = self.root.wm_geometry().split("+")
        win_x, win_y = int(parts[1]), int(parts[2])
        
        for monitor in get_monitors():
            if (monitor.x <= win_x < monitor.x + monitor.width and
                monitor.y <= win_y < monitor.y + monitor.height):
                
                return monitor

        return None
    
    def apply_window_size(self):
        self.root.geometry(f"{round(self.current_window_width*self.height_quo)}x{round(self.current_window_height*self.height_quo)}")
        ctk.set_widget_scaling(self.height_quo)
        self.root.update()   
        
    # Resize window based on monitor resolution
    def resize_window(self, window, current_monitor):
        last_monitor = current_monitor
        
        new_monitor = self.get_current_monitor()
        
        if new_monitor is not None:
            current_monitor = new_monitor
                
        if (current_monitor != last_monitor):
            self.height_quo = current_monitor.height / 1200
            
            self.apply_window_size()
            self.fonts.resize_text(self.height_quo)
        
        self.root.after(100, self.resize_window, window, current_monitor)

    def resize_widgets(self, parent, size_quo):
        for child in parent.winfo_children():
            self.resize_dimensions(child, size_quo)    
            self.resize_gaps(child, size_quo)
                
            if child.winfo_children():
                self.resize_widgets(child, size_quo)

    def resize_text(self, parent, size_quo):
        for child in parent.winfo_children():
            try:
                if "font" in child.keys():
                
                    raw_font = child.cget("font")
                    
                    if raw_font:
                        font_obj = tkfont.Font(font=raw_font)
                        
                        font_name = font_obj.actual("family")
                        current_size = font_obj.actual("size")  
                        
                        child.configure(font=(font_name, round(current_size*size_quo)))
            except:
                pass
                
            if child.winfo_children():
                self.resize_text(child, size_quo)
                
    def resize_dimensions(self, widget, size_quo):
        try:
            if "height" in widget.keys():
                if not hasattr(widget, "original_height"):
                    height = widget.cget("height")
                    
                    if height is not None:
                        widget.original_height = round(float(height))
                    else:
                        widget.original_height = widget.winfo_height()
                
                new_height = round(widget.original_height * size_quo)
                if new_height > 1:
                    widget.configure(height=new_height)
        except:
            pass
    
        try:
            if "width" in widget.keys():
                if not hasattr(widget, "original_width"):
                    width = widget.cget("width")
                    
                    if width is not None:
                        widget.original_width = round(float(width))
                    else:
                        widget.original_width = widget.winfo_width()
        
                new_width = round(widget.original_width * size_quo)
                if new_width > 1:
                    widget.configure(width=new_width)
        except Exception as e:
            print(e)  
            
    def resize_gaps(self, widget, size_quo):
        try:
            if not hasattr(widget, "original_pack_info"):
                info = widget.pack_info()
                
                widget.original_pack_info = {
                    "side": info.get("side", ctk.TOP), 
                    "anchor": info.get("anchor", ctk.CENTER),
                    "fill": info.get("fill", ""),
                    "padx": info.get("padx", 0),
                    "pady": info.get("pady", 0) 
                }
            
            if hasattr(widget.original_pack_info["padx"], "__iter__"):
                padx = widget.original_pack_info["padx"]
                padx = tuple([size_quo*x for x in padx])
            else:
                padx = widget.original_pack_info["padx"]  * size_quo
            if hasattr(widget.original_pack_info["pady"], "__iter__"):
                pady = widget.original_pack_info["pady"]
                pady = tuple([size_quo*x for x in pady])
            else:
                pady = widget.original_pack_info["pady"] * size_quo  
            
            widget.pack(
                side=widget.original_pack_info["side"], 
                anchor=widget.original_pack_info["anchor"], 
                fill=widget.original_pack_info["fill"], 
                padx=padx, 
                pady=pady
            )
        except:
            pass 
        
        if widget.winfo_children():
                self.resize_text(widget, size_quo)
          
    # Forces each widget to repaint itself (solves visual bugs)
    def force_coordinate_update(self, widget):
        for child in widget.winfo_children():
            if hasattr(child, "_draw"):
                child._draw()

            child.update() 
            
            if child.winfo_children():
                self.force_coordinate_update(child)   
             
    # Scroll logic
    def window_scroll(self, event, frame, dist):
        current_pos = frame._parent_canvas.yview()[0]
        step = 0.02
        
        if dist > 0:
            new_pos = current_pos + step
        else:
            new_pos = current_pos - step
        
        frame._parent_canvas.yview_moveto(max(new_pos, 0))
        return "break"

    def show_opening_screen(self):
        self.opening_screen_view.tkraise()

    def show_projects_screen(self):           
        self.view_sessions_view.tkraise()     
            
    def show_new_project_screen(self): 
        self.create_session_view.tkraise()
        
    def load_sessions_info(self):
        try:
            with open(env.SESSIONS_FILE, mode="r", encoding="utf-8") as file:
                try:
                    self.sessions_info = json.load(file)
                except json.decoder.JSONDecodeError:
                    self.sessions_info = []
                    return  
        except FileNotFoundError:
            self.sessions_info = []
            return
        
    def add_session_info(self, new_entry):
        if new_entry not in self.sessions_info:
            self.sessions_info.append(new_entry)
        self.save_sessions()
            
    def remove_session_info(self, entry_name):
        session_info_to_remove = next((session for session in self.sessions_info if session["name"] == entry_name), None)
        self.sessions_info.remove(session_info_to_remove)
        self.save_sessions()
        
    def add_session_ctrl(self, new_ctrl):
        if new_ctrl not in self.session_ctrls:
            self.session_ctrls.append(new_ctrl)
            
    def remove_session_ctrl(self, ctrl):
        self.session_ctrls.remove(ctrl)
        
    def add_session(self, new_session):
        if new_session not in self.sessions:
            self.sessions.append(new_session)
        
    def remove_session(self, session):
        self.sessions.remove(session)

    # Save sessions to json file
    def save_sessions(self):
        session_map = {s.session_name: s for s in self.session_ctrls}
        
        for session_info in self.sessions_info:
            name = session_info["name"]
            if name in session_map:
                session = session_map[name]
                session_info["sequence_progress"] = session.sequence_progress
                session_info["progress"] = session.progress
        
        with open(env.SESSIONS_FILE, mode="w", encoding="utf-8") as file:
            json.dump(self.sessions_info, file)
            
    def update_sessions_on_login(self):
        for i in range(len(self.session_ctrls)):
            if self.session_ctrls[i].server == self.server and self.session_ctrls[i].user == self.user:        
                self.sessions[i].on_login_config()
                    
                # Resume progress updates
                _, _, exit_code = self.ssh_controller.execute_command(f"[ -f ~/LLMPipe/{self.session_ctrls[i].session_name}.log ]")
                    
                if exit_code == 0:
                    _, stdout, _ = self.ssh_controller.ssh_client.exec_command(f"tail -f ~/LLMPipe/{self.session_ctrls[i].session_name}.log")  
                    
                    self.session_ctrls[i].resume_progress_updates(self.sessions[i], stdout, self.session_ctrls[i].sequence_progress)
                else:
                    self.session_ctrls[i].progress = 1
                    self.session_ctrls[i].sequence_progress = self.session_ctrls[i].sequence_count
                    self.sessions[i].update_finished_progress()
        
    def on_closing(self):
        self.save_sessions()
        self.ssh_controller.close_clients()
        self.root.destroy()
        
        try:
            self.root.withdraw()
        except Exception:
            pass
                
        for after_id in self.root.tk.eval('after info').split():
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass
                
        try:
            self.root.quit()
        except Exception:
            pass 
        
        try:
            self.root.destroy()  
        except Exception:
            pass