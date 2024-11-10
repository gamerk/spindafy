from PIL import Image
from spinda_optimizer import evolve, fast_evo
import json, PIL.ImageOps
from random import shuffle, seed
import numpy as np
from timeit import timeit

seed(0)

# this is definitely not the best way of doing this!
def to_spindas(filename, pop, n_generations, invert = False):
    with Image.open(filename) as target:
        target = target.convert("RGB")
        target = target.resize((target.size[0] * 2, target.size[1] * 2), resample=Image.Resampling.NEAREST)
        if invert: target = PIL.ImageOps.invert(target)

        tarr = np.array(target)

        num_x = int((target.size[0]+10)/25)
        num_y = int((target.size[1]+13)/20)

        # print(f"Size: {num_x} * {num_y}")

        tarr = np.pad(tarr, ((0, num_y*20+33 - tarr.shape[0]), (0, num_x*25+35 - tarr.shape[1]), (0, 0)))

        img = Image.new("RGBA", (39 + num_x * 25, 44 + num_y * 20))
        pids = []

        for y in range(num_y):
            pids += [[]]
            for x in range(num_x):
                # print(f"Subimage {x}|{y}")
                sub_target = tarr[y*20:y*20+33, x*25:x*25+35]
                best_spinda = fast_evo(sub_target)
                spinmage = best_spinda.render_pattern()
                img.paste(
                    spinmage,
                    (x * 25, y * 20),
                    spinmage
                )
                pids[y].append(best_spinda.get_personality())

        return (img, pids)
    
if __name__ == "__main__":
    from time import time
    (img, pids) = to_spindas("test/hutao1.bmp", 100, 10)
    # print(timeit("""to_spindas("test/test_large.png", 100, 10)""", globals=vars(), number=10) / 10)
    img.resize((img.size[0]*10, img.size[1]*10), Image.Resampling.NEAREST)#.show()
    img.save("res/test_res.png")
    with open("res/test.json", "w") as f:
        json.dump(pids, f)