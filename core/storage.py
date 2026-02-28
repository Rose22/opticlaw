import core
import os
import msgpack

DATADIR = "data"
if not os.path.exists(DATADIR):
    os.mkdir(DATADIR)

class Storage(list):
    """subclassed list that handles storage of data, uses msgpack format for speed and small size"""
    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = core.get_path(os.path.join(DATADIR, file_path))
        self.name = os.path.basename(self.path)

        if os.path.exists(self.path):
            self.load()
        else:
            with open(self.path, "wb") as f:
                f.write(b'')

    def save(self):
        """save content to file"""
        with open(self.path, "wb") as f:
            try:
                serialized = msgpack.packb(self)
                f.write(serialized)
                return True
            except Exception as e:
                core.log("error", f"error writing {self.name}: {e}")
                return False

    def load(self):
        """load content from file"""
        with open(self.path, "rb") as f:
            try:
                self.clear()
                self.extend(msgpack.unpackb(f.read()))
                return self
            except Exception as e:
                core.log("error", f"error loading {self.name}: {e}")
                return None
