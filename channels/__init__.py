import core

def get_all(respect_config: bool = True):
    import channels
    return core.module.load(channels, core.channel.Channel, respect_config=respect_config)
