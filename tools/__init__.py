import core
import tools

def get_all():
    return core.submodule.load(tools, core.tool.Tool)
