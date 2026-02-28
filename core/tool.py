class Tool:
    """Base class for tools"""

    def __init__(self, manager):
        self.channel = None # gets replaced by current channel by the manager
        self.manager = manager
