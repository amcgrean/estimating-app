import os

def activate_this(venv_dir):
    # Set VIRTUAL_ENV variable
    os.environ['VIRTUAL_ENV'] = venv_dir

    # Update PATH variable
    os.environ['PATH'] = os.path.join(venv_dir, 'bin') + ':' + os.environ['PATH']

    # Unset PYTHONHOME variable
    if 'PYTHONHOME' in os.environ:
        del os.environ['PYTHONHOME']

    # Update PS1 variable
    if 'PS1' in os.environ:
        os.environ['PS1'] = '(bidtrackenv) ' + os.environ['PS1']

# Activate the virtual environment
activate_this('/home/amcgrean/mysite/bidtrackenv')