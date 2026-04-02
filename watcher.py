import os
import time
from ingest import ingest_file

folder = "data_uploads"

processed = set()

while True:

    files = os.listdir(folder)

    for file in files:

        path = os.path.join(folder, file)

        if path not in processed:

            ingest_file(path)
            processed.add(path)

    time.sleep(10)