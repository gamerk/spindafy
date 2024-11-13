import os
import re

for file in os.listdir("adef_spinda"):
    new = f"adef_spinda/frame{int(file[5:-4]):07}.png"
    os.rename("adef_spinda/" + file, new)