import sys
import os
import json
from datetime import datetime

DIRPATHS = 0
DIRNAMES = 1
FILENAMES = 2

def generate_dev_songs_catalog():
    """ Generate a catalog of the specified directory """

    result = { }

    target_dir = "dev_songs"

    for _, dirs, _ in os.walk(target_dir):

        for song_directory in dirs:

            if song_directory.startswith("."):
                continue

            for _, _, files in os.walk(f"{target_dir}/{song_directory}"):
                for file in files:

                    if file.startswith(".") or file.endswith(".meta"):
                        print(file)
                        continue

                    file = f"{song_directory}/{file}"

                    result[file] = { }

                    modification_sec = os.path.getmtime(f"{target_dir}/{file}")
                    m_date = str(datetime.fromtimestamp(modification_sec))

                    result[file]["ModificationDate"] = m_date
                    result[file]["Size"] = os.path.getsize(f"{target_dir}/{file}")

    y = json.dumps(result, indent=4)

    with open(f"{target_dir}/catalog.json", "w") as index:
        index.write(y)
