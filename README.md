# LLMPipeGUI
A graphical user interface for using DNA language models using customtkinter. This project is meant to make the usage of DNA language models easier and more intuitive for people that are less technical.

## Requirements
You will need a Linux System with a graphics card that has CUDA cores to run the LLMs.
Python 3.12 or newer is required on the system running the GUI.

## Quickstart

### Download
You can find the downloads on the [Release Page](https://github.com/SergiuM002/LLMPipeGUI/releases/latest).

## Building

### Creating the environment
Create the venv environment in the project root using `python3 -m venv .venv` and activate it.

### Building via Briefcase
Install briefcase with `pip install briefcase` and package the project with `briefcase package`. The built package should be in "dist/".

### Building via Pyinstaller
Install the requirements with `pip install -r requirements.txt` and pyinstaller with `pip install pyinstaller`. Then, package the program with `pyinstaller spec/main.spec`. The executable should be in "dist/LLMPipeGUI/".

## Usage
To do anything, you will first have to install everything that the LLMs need to run on a server. To do that, go to "Remote Install", enter the credentials and click install.
After that is finished, you can run the LLMs in the "New Session" screen and view running sessions in the "View Sessions" screen.