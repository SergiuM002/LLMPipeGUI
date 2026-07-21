# LLMPipeGUI
A graphical user interface for using DNA language models using customtkinter. This project is meant to make the usage of DNA language models easier and more intuitive for people that are less technical.

## Quickstart

### Cloning the repository
Clone the repository to your system using `git clone <repository-link>`.

### Creating the environment
Create the venv environment using `python -m venv .venv`, activate it and install the required packages from the requirements.txt with `pip install -r requirements.txt`.

### Setting up the remote part
Use the "install_llm_pipe.py" script in the "install script" directory to install the environment and the script used to run the LLM on your server.

### Use the GUI
Now you can launch the GUI from "main.py" and use the different LLMs to score your sequences.

## Building the program
If you want to not have to launch the scripts from within the environment in the terminal, follow these steps to create executables.

### Installing Pyinstaller
You will have to manually install the pyinstaller package using `pip install pyinstaller`, since it is not included in the requirements.

### Using the spec files
To build the GUI program, run `pyinstaller spec/main.spec`. The executable will be in "dist/main".
Similarly, you build the install program with `pyinstaller spec/install_llm_pipe.spec`. The executable will be in "dist/install_llm_pipe".