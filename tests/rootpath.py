import os

def root_path():
    return os.path.dirname(__file__)

def data_path():    
    return os.path.join(os.path.dirname(__file__), "data")
 
def config_path():    
    return os.path.join(os.path.dirname(__file__), "config")

def add_root_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)

def add_data_path(fname):
    return os.path.join(os.path.dirname(__file__), "data", fname)
 
def add_config_path(fname):
    return os.path.join(os.path.dirname(__file__), "config", fname)
