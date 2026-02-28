import core
import os
import sys
import traceback

def log(category: str, msg: str):
    """simple console log"""
    print(f"[{category.upper()}] {msg}")

def log_error(msg: str, e: Exception):
    """console log but with extra spice for errors"""
    log("error", f"{msg}: {e} | {e.__traceback__.tb_frame.f_code.co_filename}, {e.__traceback__.tb_frame.f_code.co_name}, ln:{e.__traceback__.tb_lineno}")
    #traceback.print_exception(e, limit=2, file=sys.stdout)

def get_path(path: str = ""):
    """get path relative to the project root directory. returns root path if no path is specified."""
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        path
    ))
