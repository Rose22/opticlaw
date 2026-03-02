import core
import core.module

def get_all(respect_config: bool = True):
    import modules
    return core.module.load(modules, core.module.Module, respect_config=respect_config)
