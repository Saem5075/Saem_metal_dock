#!/usr/bin/env python
import os,sys,subprocess

def find_command_path(command):
    try:
        if sys.platform.startswith('win'):
            # On Windows, use the 'where' command
            result = subprocess.check_output(['where', command], universal_newlines=True)
        else:
            # On Unix-based systems, use the 'which' command
            result = subprocess.check_output(['which', command], universal_newlines=True)

        # Remove any leading/trailing whitespace and return the path
        return result.strip()
    except subprocess.CalledProcessError:
        print(f"Error: The command '{command}' was not found in your system's PATH.")
        sys.exit(1)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))[:-11] # Project Root
os.environ['ROOT_DIR']=ROOT_DIR

os.environ['OBABEL']=find_command_path('obabel')
os.environ['PDB2PQR']=find_command_path('pdb2pqr30')
os.environ['MGLTOOLS']=os.path.join(os.environ['ROOT_DIR'],'external','AutoDockTools')
os.environ['PYTHON_2']=find_command_path('python2.7')
os.environ['PYTHON_3']=find_command_path('python3')
