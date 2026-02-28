import core
import os

def log(category: str, msg: str):
    """simple console log"""
    print(f"[{category.upper()}] {msg}")

def get_path(path: str = ""):
    """get path relative to the project root directory. returns root path if no path is specified."""
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        path
    ))
