import paramiko
import socket
import json
import traceback
import config.environment as env
import threading

class LoginWindowController:
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        
    def autofill_saved_info(self, view):
        try:
            with open(env.LASTLOGIN_FILE, mode="r", encoding="utf-8") as file:
                try:
                    login_info = json.load(file)
                except json.decoder.JSONDecodeError:
                    return
        except FileNotFoundError:
            return
                
        if login_info:
            view.fill_saved_info(login_info)
        
    def confirm_login(self, view):
        if not view.server_entry.get() or not view.username_entry.get() or not view.password_entry.get():
            self.main_ctrl.root.after(0, view.show_fields_error_message_box)
            self.main_ctrl.root.after(0, view.enable_confirm_button)
            
        server = view.server_entry.get()
        username = view.username_entry.get()
        password = view.password_entry.get()
            
        self.login_thread = threading.Thread(target=self.attempt_login, args=(view, server, username, password))
        self.login_thread.start()        
                
    def attempt_login(self, view, server, username, password):
        login_info = ({
                    "server": server,
                    "username": username
            })

        try:
            self.main_ctrl.ssh_controller.login(
                server, 
                username, 
                password
            ) 
            self.main_ctrl.logged_in = True
            self.main_ctrl.server = login_info["server"]
            self.main_ctrl.user = login_info["username"]
            
            self.main_ctrl.create_session_view.update_login()
            self.main_ctrl.view_sessions_view.update_login()
            
            with open(env.LASTLOGIN_FILE, mode="w", encoding="utf-8") as file:
                json.dump(login_info, file) 
                
            self.main_ctrl.root.after(0, view.destroy)
        except (paramiko.AuthenticationException, Exception) as e:
            if isinstance(e, paramiko.AuthenticationException): 
                msg = "Wrong username or password."
            elif isinstance(e, (socket.timeout, socket.gaierror)):
                msg = "Wrong hostname."
            else:
                print(traceback.format_exc())
                msg = "Error: " + str(e)
                
            self.main_ctrl.root.after(0, view.show_input_error_message_box, msg)
            self.main_ctrl.root.after(0, view.enable_confirm_button)
        
    def clean_msg_box_bindings(self, event, view):
        if event.widget == view.msg_box:
            view.bind_all("<Return>", lambda e: view.confirm_button_clicked())