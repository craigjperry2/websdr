# Craig's Web SDR

View the 2-metre VHF amateur radio band in real time via a cheap RTL SDR
dongle with appropriate antenna.

# Developer Setup

There are 3 sub-projects:

* notebook: Jupyter notebooks exploring how to work with PyRTLSDR
* backend: FastAPI based RESTful SDR server, hosts the SDR used by clients
* frontend: Svelte based SDR client

## notebooks Sub-Project

### Requirements

* Windows, Linux or MacOS
* Python 3.7+

### Setup

I've created separate virtual envs for backend and notebook, that's not
strictly required so feel free to use one common venv if you prefer.

1. `cd notebook`
1. Create a Python virtualenv `python -m venv notebook/venv` and activate it
1. Install the dependencies into the venv, I had to update pip first
  1. `python -m pip install --U pip`
  1. `pip install -r requirements.txt`
1. Launch jupyter: `jupyter` (i'm using vscode's notebook support instead)

## backend Sub-Project

Requirements and setup are the same as described under the notebook Sub-Project
above, with the exception of the last step - Jupyter is not used here.
