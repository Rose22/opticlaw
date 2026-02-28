import core.config
import core.openai_api
import core.manager
import core.channel
import core.tools
import core.scheduler

def log(category: str, msg: str):
    """simple console log"""
    print(f"[{category.upper()}] {msg}")
