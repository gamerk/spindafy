import os
import re

for file in os.listdir("adef_spinda"):
    # new = f"adef_spinda/frame{int(file[5:-4]):07}.png"
    # os.rename("adef_spinda/" + file, new)
    if len(file[5:-4]) < 7 or int(file[5:-4]) > 32000:
        os.unlink(f"adef_spinda/{file}")