import subprocess

def validate(path):
    try:
        subprocess.check_output(["python","-m","py_compile",path])
        return True
    except:
        return False
