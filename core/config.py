import os
import yaml

config = {}

if not os.path.exists("config.yaml"):
    open("config.yaml", 'w').write("")

try:
    with open("config.yaml") as f:
        config = yaml.safe_load(f.read())
except Exception as e:
    print(f"error loading config file:\n{e}")
    exit(1)
