from llmpipegui.ui.views.login_window import LoginWindow
from llmpipegui.controllers.views.login_window_controller import LoginWindowController
import llmpipegui.config.environment as env
import threading


class RemoteInstallWindowController:
    """Coordinates the remote installation window."""
    def __init__(self, main_ctrl):
        self.main_ctrl = main_ctrl
        
    def connect_view(self, view):
        """Saves a reference to the corresponding view."""
        self.view = view
        
    def show_login_window(self):
        """Opens a login window."""
        LoginWindow(LoginWindowController(self.main_ctrl), self.view)
        
    def start_remote_install(self):
        """Starts a thread for the remote install."""
        self.worker_thread = threading.Thread(target=self.remote_install)
        self.worker_thread.start()
    
    def remote_install(self):  
        """Installs the necessary packages and script on the logged in server."""
        ssh_controller = self.main_ctrl.ssh_controller
        
        def run_step(command: str, progress: int, message: str, fail_message: str):
            """
            Runs an install step.
            command: command to be run
            progress: progress percentage to be shown when the step is finished
            message: message to be shown on step start
            fail_message: popup message to be shown on error
            """
            self.view.show_install_message(message)
            _, err, error_code = ssh_controller.execute_command(command)
            
            if error_code != 0:
                print(err)
                self.view.show_popup_error(f"{fail_message}:\n{err}")
                self.view.show_error_text()
                return False
            
            self.view.show_install_progress(progress)
            return True
        
        self.view.show_install_progress_start()
        self.view.show_install_progress(0, "Downloading miniconda...")
        
        CONDA_BIN = "$HOME/miniconda3/bin/conda"
        CONDA_INIT = "source $HOME/miniconda3/etc/profile.d/conda.sh && "
        ENV_DIR = "$HOME/miniconda3/envs/plantcad_env"
        ENV_BIN = f"{ENV_DIR}/bin"
        ENV_PIP = f"{ENV_BIN}/pip"
         
        if not ssh_controller.remote_dir_exists("miniconda3") and not run_step(
            "curl -L -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && "
            "bash Miniconda3-latest-*.sh -b -p $HOME/miniconda3 -u && "
            "rm Miniconda3-latest-*.sh",
            10,   
            "Downloading miniconda...",
            "Miniconda failed to install"
        ):
            return
        self.view.show_install_progress(10)


        if not run_step(
            f"{CONDA_INIT}"
            f"{CONDA_BIN} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && "
            f"{CONDA_BIN} tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r",
            20,
            "Accepting Anaconda channel terms...",
            "Failed to accept miniconda TOS"
        ):
            return
        
        package_check = (
            f'{ENV_BIN}/python -c "import importlib.metadata as m, sys; '
            "versions = {d.metadata.get('Name', '').lower().replace('_', '-'): d.version "
            "for d in m.distributions()}; "
            "expected = {'torch': '2.3.1+cu121', 'torchvision': '0.18.1+cu121', 'torchaudio': '2.3.1+cu121', "
            "'causal-conv1d': '1.5.0.post8', 'mamba-ssm': '2.2.2', 'transformers': '4.40.0', "
            "'pyvcf3': None, 'scipy': '1.12.0', 'biopython': None, 'xgboost': '2.0.3', "
            "'scikit-learn': '1.4.0', 'matplotlib': None, 'gpn': None}; "
            "missing = [n for n, v in expected.items() if not versions.get(n) or "
            "(v is not None and versions[n] != v)]; "
            "sys.exit(1 if missing else 0)\""
        )
        _, _, package_check_error = ssh_controller.execute_command(package_check)
        packages_installed = package_check_error == 0

        if packages_installed:
            self.view.show_install_message("Uploading the remote script...")
            self.view.show_install_progress(95)
        else:
            if not run_step(
                f"{CONDA_INIT}"
                f"if [ -d \"$HOME/miniconda3/envs/plantcad_env\" ]; then {CONDA_BIN} env remove -n plantcad_env -y; fi && "
                f"{CONDA_BIN} create -y --name plantcad_env python=3.10.19 && "
                f"{CONDA_BIN} install -n plantcad_env -c nvidia -c bioconda -y cuda-nvcc cuda-toolkit mafft",
                40,
                "Creating the plantcad environment...",
                "Failed to set up environment"
            ):
                return

            if not run_step(
                f"{ENV_PIP} install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 "
                "--index-url https://download.pytorch.org/whl/cu121",
                65,
                "Installing PyTorch...",
                "Failed to install PyTorch"
            ):
                return

            if not run_step(
                f"export CUDA_HOME={ENV_DIR} && "
                f"export PATH={ENV_BIN}:$PATH && "
                f"export LD_LIBRARY_PATH={ENV_DIR}/lib:$LD_LIBRARY_PATH && "
                f"{ENV_PIP} install https://github.com/Dao-AILab/causal-conv1d/releases/download/v1.5.0.post8/causal_conv1d-1.5.0.post8+cu12torch2.3cxx11abiFALSE-cp310-cp310-linux_x86_64.whl",
                70,
                "Installing causal-conv1d...",
                "Failed to install causal-conv1d"
            ):
                return

            if not run_step(
                f"{CONDA_INIT}"
                f"export PATH={ENV_BIN}:$PATH && "
                f"{ENV_PIP} install mamba-ssm==2.2.2 transformers==4.40.0 git+https://github.com/dridk/PyVCF3.git@master scipy==1.12.0 biopython xgboost==2.0.3 scikit-learn==1.4.0 matplotlib --no-build-isolation",
                80,
                "Installing additional Python packages...",
                "Failed to install Python package"
            ):
                return

            if not run_step(
                "echo -e 'torch==2.3.1\ntorchvision==0.18.1\ntorchaudio==2.3.1\ntransformers==4.40.0' > constraints.txt && "
                f"{ENV_PIP} install git+https://github.com/SilvanCodes/gpn.git -c constraints.txt && "
                "rm constraints.txt",
                90,
                "Installing GPN...",
                "Failed to install GPN"
            ):
                return

        if not run_step("mkdir -p ~/LLMPipe", 95, "Uploading the remote script...", "Failed to upload remote script"):
            return
                    
        try:
            ssh_controller.sftp_client.put(str(env.REMOTE_SCRIPT_DIR), "LLMPipe/llm_pipe.py")
        except Exception as err:
            print(err)
            self.view.show_popup_error(str(err))
            self.view.show_error_text()
            return

        self.view.show_install_progress(100)
        self.view.show_install_message("Installed.")