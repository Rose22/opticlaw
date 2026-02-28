import core
import channels

def get_all():
    return core.submodule.load(channels, core.channel.Channel)
