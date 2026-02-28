import os
import yaml
import core

config = {}

default_config = {
    "api_base": "http://localhost:11434/v1",
    "api_key": "KEY_HERE",
    "model": "MODEL_HERE"
}

config_path = core.get_path("config.yaml")
if not os.path.exists(config_path):
    open(config_path, 'w').write(yaml.dump(default_config))

try:
    with open(config_path) as f:
        config = yaml.safe_load(f.read())
except Exception as e:
    print(f"error loading config file:\n{e}")
    exit(1)

def get(*args, **kwargs):
    """shorthand for accessing config values"""

    return config.get(*args, **kwargs)
