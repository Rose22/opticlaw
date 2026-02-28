class Tool:
    """Base class for tools"""

    def __init__(self, manager):
        self.channel = None # gets replaced by current channel by the manager
        self.manager = manager

    def result(self, data, error=False):
        """unified way of returning tool results"""
        print({
            "status": "success" if not error else "error",
            "content": data
        })

        return {
            "status": "success" if not error else "error",
            "content": data
        }
