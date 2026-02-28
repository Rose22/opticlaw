import core

class Memory:
    """manages the AI's memory"""

    # TODO: add real memory system

    def __init__(self):
        self._mem = core.storage.Storage("memory")
        self._hist = core.storage.Storage("history")

    def get_persistent_memories(self):
        return ""
