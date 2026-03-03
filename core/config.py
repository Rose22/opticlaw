import os
import yaml
import core
import modules
import channels

config = core.storage.StorageDict("config", "yaml")

default_config = {
    "api_url": "http://localhost:11434/v1",
    "api_key": "KEY_HERE",
    "model": "MODEL_HERE",
    "webui_host": "localhost",
    "webui_port": "5000",
    "channels": ["cli", "webui"],
    "channels_disabled": [],
    "modules": [],
    "modules_disabled": [],
    "modules_disable_prompts": [],
    "max_turns": 20,
    "context_window": True
}

for channel in channels.get_all(respect_config=False):
    channel_name = core.module.get_name(channel)
    if channel == "debug":
        continue

    if channel_name != "cli":
        default_config["channels_disabled"].append(channel_name)

for module in modules.get_all(respect_config=False):
    module_name = core.module.get_name(module)
    if module_name in ("identity", "memory", "scheduler"):
        default_config["modules"].append(module_name)
    else:
        default_config["modules_disabled"].append(module_name)

if not config:
    config.load(default_config)
    config.save()

def get(*args, **kwargs):
    """shorthand for accessing config values"""

    return config.get(*args, **kwargs)
