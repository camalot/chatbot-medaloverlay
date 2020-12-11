import sys
import json
import os
import re
import random
import datetime
import glob
import time
import shutil
import tempfile
import codecs

UIConfigFile = os.path.join(os.path.dirname(__file__), "../script/UI_Config.json")
DefaultsFile = os.path.join(os.path.dirname(__file__), "defaults.js")

def main():
    defaults = dict()
    with codecs.open(UIConfigFile, encoding="utf-8-sig", mode="r") as f:
        ui = json.load(f, encoding="utf-8")
    for key in ui:
        if 'value' in ui[key]:
            try:
                defaults[key] = ui[key]['value']
            except Exception as ex:
                if key != "output_file":
                    print(f"could not find {key}")
                    print(ex)
    values = json.dumps(defaults, indent = 2)
    f = open(DefaultsFile, "w")
    f.write("var DEFAULT_SETTINGS = ")
    f.write(values)
    f.write(";")
    f.close()

if __name__ == "__main__":
    main()
