import os
import re
import json

# for file in os.listdir("adef_spinda"):
#     # new = f"adef_spinda/frame{int(file[5:-4]):07}.png"
#     # os.rename("adef_spinda/" + file, new)
#     if len(file[5:-4]) < 7 or int(file[5:-4]) > 32000:
#         os.unlink(f"adef_spinda/{file}")

pids = []

all_files = os.listdir("badspinda/pids")

for fno, file in enumerate(all_files):
    if fno % 50 == 0:
        print(f"{fno} / {len(all_files)} ({fno / len(all_files) * 100}%)")
    fp = open("badspinda/pids/" + file)
    output: list[list[int]] = json.load(fp)
    for row in output:
        pids += row
    fp.close()

print(len(pids))

hist = sorted(list(set(pids)), key=lambda i: pids.count(i), reverse=True)

for pid in hist:
    print(f"{pid} ({pids.count(pid)})")
