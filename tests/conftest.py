import os

os.environ["PRAMAAN_OFFLINE"] = "1"  # tests never call the model unless they pass a reader
