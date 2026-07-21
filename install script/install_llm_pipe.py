import platform
import paramiko
import socket
import sys
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from pathlib import Path
from screeninfo import get_monitors

# Resizes the Windows when dragged to a monitor with a different resolution
def resize_window(window, current_monitor):
    try:
        x = window.winfo_x()
        y = window.winfo_y()
        last_monitor = current_monitor
        
        for monitor in get_monitors():
            if 0 <= x - monitor.x <= monitor.width and 0 <= y - monitor.y <= monitor.height:
                current_monitor = monitor
                
        if (current_monitor != last_monitor):
            height_quo = current_monitor.height / last_monitor.height

            window_height = round(window.winfo_height() * height_quo)
            window_width = window_height
        
            window.geometry(f"{window_width}x{window_height}")
            
            resize_text(window, height_quo)
            resize_gaps(window, height_quo)
            resize_heights(window, height_quo)
    except:
        pass
       
    root.after(100, resize_window, window, current_monitor)

   
def resize_text(parent, size_quo):
    for child in parent.winfo_children():
        try:
            child.configure(font=(child.cget("font")[0], round(child.cget("font")[1] * size_quo)))
        except:
            pass
            
        if child.winfo_children():
            resize_text(child, size_quo)
        
# Resizes widget heights for those that have them
def resize_heights(parent, size_quo):
    for child in parent.winfo_children():
        try:
            child.configure(height=round(child.cget("height") * size_quo))
        except:
            pass
            
        if child.winfo_children():
            resize_heights(child, size_quo) 
        
# Resizes the padding of the widgets
def resize_gaps(parent, size_quo):
    for child in parent.winfo_children():
        try:
            info = child.pack_info()
            side = info.get("side", ctk.TOP)
            anchor = info.get("anchor", ctk.CENTER)
            fill = info.get("fill", "")
            
            if hasattr(info.get("padx", 0), "__iter__"):
                padx = info.get("padx", 0) 
                padx = tuple([size_quo*x for x in padx])
            else:
                padx = info.get("padx", 0)  * size_quo
            if hasattr(info.get("pady", 0), "__iter__"):
                pady = info.get("pady", 0) 
                pady = tuple([size_quo*x for x in pady])
            else:
                pady = info.get("pady", 0) * size_quo  
            
            child.pack(side=side, anchor=anchor, fill=fill, padx=padx, pady=pady)
        except:
            pass
            
        if child.winfo_children():
            resize_gaps(child, size_quo) 

def create_login_window():
    root.login_win = ctk.CTkToplevel()
    root.login_win.attributes("-topmost", True)
    root.login_win.title("Login")
    login_win_width = round(300*height_quo)
    login_win_height = round(350*height_quo)
    root.login_win.geometry(f"{login_win_width}x{login_win_height}+{round(center_x+login_win_width/2)}+{round(center_y+login_win_height/2)}")
    root.login_win.resizable(False, False)
    
    root.login_scrollframe = ctk.CTkScrollableFrame(root.login_win, fg_color="transparent")
    root.login_scrollframe.pack(fill="both", expand=True)
    
    server_label = ctk.CTkLabel(root.login_scrollframe, text="Server", font=("Roboto", 20))
    server_label.pack(pady=(20*height_quo, 0))
    
    server_entry = ctk.CTkEntry(root.login_scrollframe, font=("Roboto", 16), height=28*height_quo)
    server_entry.pack(fill="x", padx=20*height_quo)
    root.after(100, server_entry.focus_force)

    username_label = ctk.CTkLabel(root.login_scrollframe, text="Username", font=("Roboto", 20))
    username_label.pack(pady=(20*height_quo, 0))
    
    username_entry = ctk.CTkEntry(root.login_scrollframe, font=("Roboto", 16), height=28*height_quo)
    username_entry.pack(fill="x", padx=20*height_quo)
    
    password_label = ctk.CTkLabel(root.login_scrollframe, text="Password", font=("Roboto", 20))
    password_label.pack(pady=(20*height_quo, 0))
    
    password_entry = ctk.CTkEntry(root.login_scrollframe, font=("Roboto", 16), show="*", height=28*height_quo)
    password_entry.pack(fill="x", padx=20*height_quo)
    
    confirm_button = ctk.CTkButton(
        root.login_scrollframe, 
        text="Login", 
        font=("Roboto", 20), 
        command=lambda: confirm_login(server_entry, username_entry, password_entry, root.login_win),
        height=32*height_quo,
        fg_color="#40921A",
        text_color="white",
        hover_color="#367E15"
    )
    confirm_button.pack(anchor=ctk.CENTER, padx=10, pady=40)
    
    # Linux requires manual binding for scrolling
    if platform.system() == "Linux":
        root.login_win.bind_all("<Button-4>", lambda e: login_scroll(e, -1))        
        root.login_win.bind_all("<Button-5>", lambda e: login_scroll(e, 1))  
    
    root.login_win.bind_all("<Return>", lambda e: confirm_login(server_entry, username_entry, password_entry, root.login_win))
    resize_window(root.login_win, current_monitor)

# Confirms login or gives an error message
def confirm_login(s_entry, u_entry, p_entry, parent):
    if not s_entry.get() or not u_entry.get() or not p_entry.get():
        msg = CTkMessagebox(
            master=parent,
            title="Error",
            message="Please fill out all the fields.",
            icon="cancel",
            button_color="#40921A",
            button_hover_color="#367E15"
        )
        msg.bind("<Return>", lambda e: msg.destroy())
    else:
        root.client = paramiko.SSHClient()
        root.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            root.client.connect(hostname=s_entry.get(), username=u_entry.get(), password=p_entry.get(), timeout=5)
            root.login_win.destroy()
            login_button.configure(state="disabled")
            install_button.configure(state="normal")
            login_text.set("logged in ✓")
        except paramiko.AuthenticationException:
            msg = CTkMessagebox(
                master=parent,
                title="Error",
                message="Wrong username or password.",
                icon="cancel",
                button_color="#40921A",
                button_hover_color="#367E15"
            ) 
        except socket.timeout:
            msg = CTkMessagebox(
                master=parent,
                title="Error",
                message="Wrong hostname.",
                icon="cancel",
                button_color="#40921A",
                button_hover_color="#367E15"
            ) 
            
        except Exception as e:
            msg = CTkMessagebox(
                master=parent,
                title="Error",
                message=f"Error: {e}",
                icon="cancel",
                button_color="#40921A",
                button_hover_color="#367E15"
            )  
            
def login_scroll(event, dist):            
    current_pos = root.login_scrollframe._parent_canvas.yview()[0]
    
    step = 0.02
    
    if dist > 0:
        new_pos = current_pos + step
    else:
        new_pos = current_pos - step
    
    root.login_scrollframe._parent_canvas.yview_moveto(new_pos)
    
def install():  
    install_button.configure(state="disabled")
    progress_text.set("installing...")
    progress_label.update()
    progress_bar.pack(padx=30)
    progress_bar.update()
    
    sftp = root.client.open_sftp()
    CONDA_BIN = "$HOME/miniconda3/bin/conda"
    CONDA_INIT = "source $HOME/miniconda3/etc/profile.d/conda.sh && "
    
    try:
        sftp.stat("miniconda3")
    except FileNotFoundError:
        stdin, stdout, stderr = root.client.exec_command(
            "curl -L -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && "
            "bash Miniconda3-latest-*.sh -b -p $HOME/miniconda3 -u && "
            "rm Miniconda3-latest-*.sh"
        )
        exit_status = stdout.channel.recv_exit_status()
    
        if exit_status == 0:
            progress_bar.set(0.1)
            progress_bar.configure(progress_color="#1f538d")        
            progress_bar.update()
        else:
            progress_text.set("something went wrong")
            progress_label.update()
            error_msg = stderr.read().decode()
            output_msg = stdout.read().decode()
            print(f"STDOUT: {output_msg}")
            print(f"STDERR: {error_msg}")
        
    stdin, stdout, stderr = root.client.exec_command(
        f"{CONDA_INIT}"
        f"{CONDA_BIN} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && "
        f"{CONDA_BIN} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r"
    )
    
    print(stderr.read().decode())

    progress_bar.set(0.2)
    progress_bar.configure(progress_color="#1f538d")    
    progress_bar.update()
    
    try:
        sftp.stat("miniconda3/envs/plantcad_env")
        env_exists = True
    except FileNotFoundError:
        env_exists = False
    
    remove_cmd = f"{CONDA_BIN} env remove -n plantcad_env -y && " if env_exists else ""
    
    stdin, stdout, stderr = root.client.exec_command(
        f"{CONDA_INIT}"
        f"{remove_cmd}"
        f"{CONDA_BIN} create -y --name plantcad_env python=3.10.19 && "
        f"{CONDA_BIN} install -n plantcad_env -c nvidia -c bioconda -y cuda-nvcc cuda-toolkit mafft"  
    )
    
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status == 0:
        progress_bar.set(0.4)
        progress_bar.update()
    else:
        progress_text.set("something went wrong")
        progress_label.update()
        error_msg = stderr.read().decode()
        output_msg = stdout.read().decode()
        print(f"STDOUT: {output_msg}")
        print(f"STDERR: {error_msg}")
        
    ENV_DIR = "$HOME/miniconda3/envs/plantcad_env"
    ENV_BIN = f"{ENV_DIR}/bin"
    ENV_PIP = f"{ENV_BIN}/pip"

    stdin, stdout, stderr = root.client.exec_command(
        f"{ENV_PIP} install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        progress_bar.set(0.65)
        progress_bar.update()
    else:
        progress_text.set("something went wrong")
        progress_label.update()
        error_msg = stderr.read().decode()
        output_msg = stdout.read().decode()
        print(f"STDOUT: {output_msg}")
        print(f"STDERR: {error_msg}")
        
    stdin, stdout, stderr = root.client.exec_command(
        f"export CUDA_HOME={ENV_DIR} && "
        f"export PATH={ENV_BIN}:$PATH && "
        f"export LD_LIBRARY_PATH={ENV_DIR}/lib:$LD_LIBRARY_PATH && "
        f"{ENV_PIP} install https://github.com/Dao-AILab/causal-conv1d/releases/download/v1.5.0.post8/causal_conv1d-1.5.0.post8+cu12torch2.3cxx11abiFALSE-cp310-cp310-linux_x86_64.whl"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        progress_bar.set(0.7)
        progress_bar.update()
    else:
        progress_text.set("something went wrong")
        progress_label.update()
        error_msg = stderr.read().decode()
        output_msg = stdout.read().decode() 
        print(f"STDOUT: {output_msg}")
        print(f"STDERR: {error_msg}")
        
        
    stdin, stdout, stderr = root.client.exec_command(
        f"{CONDA_INIT}"
        f"export PATH={ENV_BIN}:$PATH && "
        f"{ENV_PIP} install mamba-ssm==2.2.2 transformers==4.40.0 git+https://github.com/dridk/PyVCF3.git@master scipy==1.12.0 biopython xgboost==2.0.3 scikit-learn==1.4.0 matplotlib --no-build-isolation"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        progress_bar.set(0.8)
        progress_bar.update()
    else:
        progress_text.set("something went wrong")
        progress_label.update()
        error_msg = stderr.read().decode()
        output_msg = stdout.read().decode()
        print(f"STDOUT: {output_msg}")
        print(f"STDERR: {error_msg}")
        
    stdin, stdout, stderr = root.client.exec_command(
        f"{ENV_PIP} install --quiet git+https://github.com/SilvanCodes/gpn.git"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        progress_bar.set(0.95)
        progress_bar.update()
        
        root.client.exec_command("mkdir -p ~/LLMPipe", get_pty=True)
    
        stdin, stdout, stderr = root.client.exec_command("pwd")
        home_dir = stdout.read().decode().strip()   
        if getattr(sys, 'frozen', False):
            BASE_DIR = Path(sys._MEIPASS)
        else:
            BASE_DIR = Path(__file__).resolve().parent
        REMOTE_SCRIPT_DIR = BASE_DIR / "remote script" / "llm_pipe.py"
        sftp.put(str(REMOTE_SCRIPT_DIR), f"{home_dir}/LLMPipe/llm_pipe.py")
        
        progress_text.set("installed")
        progress_label.update()
        progress_bar.set(1)
        progress_bar.update()
    else:
        progress_text.set("something went wrong")
        progress_label.update()
        error_msg = stderr.read().decode()
        output_msg = stdout.read().decode()
        print(f"STDOUT: {output_msg}")
        print(f"STDERR: {error_msg}")
       
monitors = get_monitors()       
            
current_monitor = monitors[0]

for m in monitors:
    if m.is_primary:
        current_monitor = m

window_height = int(current_monitor.height/4.5)
window_width = int(window_height*0.9)

center_x = int(current_monitor.width/2 - window_width/2)
center_y = int(current_monitor.height/2 - window_height/2)

height_quo = current_monitor.height/1200
            
root = ctk.CTk()
root.title("install")
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
root.resizable(False, False)

login_text = ctk.StringVar(root, "not logged in ✕")
login_label = ctk.CTkLabel(root, textvariable=login_text)
login_label.pack(padx=0, pady=(45*height_quo, 0))

login_button = ctk.CTkButton(
    root, 
    text="login", 
    command=create_login_window,
    fg_color="#40921A",
    text_color="white",
    hover_color="#367E15"
)
login_button.pack(padx=5*height_quo, pady=(5*height_quo, 40*height_quo))

install_button = ctk.CTkButton(
    root, 
    text="install", 
    state="disabled", 
    command=install,
    fg_color="#40921A",
    text_color="white",
    hover_color="#367E15"
)
install_button.pack(padx=5*height_quo)

progress_text = ctk.StringVar(root, "")
progress_label = ctk.CTkLabel(root, textvariable=progress_text)
progress_label.pack(pady=(5*height_quo, 0))

progress_bar = ctk.CTkProgressBar(root)
progress_bar.set(0)
progress_bar.configure(progress_color=progress_bar.cget("fg_color"))

root.mainloop()