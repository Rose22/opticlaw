import core
import os
import msgpack

DATADIR = "data"
if not os.path.exists(DATADIR):
    os.mkdir(DATADIR)

class Storage():
    """handles storage of data, uses msgpack format for speed and small size"""
    def __init__(self, file_path):
        self.path = core.get_path(os.path.join(DATADIR, file_path))
        self.name = os.path.basename(self.path)
        self.data = {}

        if os.path.exists(self.path):
            self.data = self.load()
        else:
            open(self.path, "wb").write(bytes).close()

    def save(self):
        with open(self.path, "wb") as f:
            try:
                serialized = msgpack.packb(self.data)
                f.write(serialized)
                return True
            except Exception as e:
                core.log("error", f"error writing {self.name}: {e}")
                return False

    def load(self):
        with open(self.path, "rb") as f:
            try:
                self.data = msgpack.unpackb(f.read())
                return True
            except Exception as e:
                core.log("error", f"error loading {self.name}: {e}")
                return False
