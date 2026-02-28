import core

test_stor = core.storage.Storage("testfile")
test_stor.load()
print(test_stor.data)
