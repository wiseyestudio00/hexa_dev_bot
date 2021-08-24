import sys
import os
import json
from datetime import datetime

DIRPATHS = 0
DIRNAMES = 1
FILENAMES = 2

def generate_catalog():
    """ Generate the lastest DevSong Catalog and write the file. """
    
    result = { }

    song_directories = next(os.walk('.'))[DIRNAMES]

    for song_direcory in song_directories:
        if song_direcory.startswith("."):
            continue

        files = next(os.walk(song_direcory))[FILENAMES]

        for file in files:

            if file.startswith(".") or file.endswith(".meta"):
                continue

            file_path = f"{song_direcory}/{file}"
            
            result[file_path] = { }
            
            modification_sec = os.path.getmtime(file_path)
            m_date = str(datetime.fromtimestamp(modification_sec))

            result[file_path]["ModificationDate"] = m_date
            result[file_path]["Size"] = os.path.getsize(file_path)


    y = json.dumps(result, indent=4)

    with open("catalog.json", "w") as index:
        index.write(y)