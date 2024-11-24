from PIL import Image
from spinda_optimizer import evolve, fast_evo, PREDEFINED
import json, PIL.ImageOps
import numpy as np
from timeit import timeit
from spindafy import SpindaConfig
import cv2
from time import sleep


to_prerender = [*PREDEFINED.values(), 8384767, 1044735]
prerendered = {pid: SpindaConfig.from_personality(pid).render_pattern() for pid in to_prerender}

# this is definitely not the best way of doing this!
def to_spindas(filename, pop, n_generations, invert = False):
    with Image.open(filename) as target:
        target = target.convert("L")
        target = target.resize((target.size[0] // 2, target.size[1] // 2), resample=Image.Resampling.NEAREST)
        if invert: target = PIL.ImageOps.invert(target)

        num_x = int((target.size[0]+10)/25)
        num_y = int((target.size[1]+13)/20)

        canny = cv2.Canny(np.array(target), 50, 150)
        canny = cv2.dilate(canny, np.full((10, 10), 1))

        tarr = np.zeros((num_y*20+33, num_x*25+35), dtype=np.bool)
        tarr[:target.size[1], :target.size[0]] = canny

        img = Image.new("RGBA", (39 + num_x * 25, 44 + num_y * 20))
        pids = []

        for y in range(num_y):
            pids.append([])
            for x in range(num_x):
                sub_target = tarr[y*20:y*20+33, x*25:x*25+35]

                (_, best_spinda) = evolve(sub_target, pop_size=0, n_gens=0)
                # print(best_spinda.get_difference(sub_target))

                if best_spinda.get_personality() in prerendered:
                    spinmage = prerendered[best_spinda.get_personality()]
                    # print(best_spinda.get_personality(), best_spinda.get_difference(sub_target))
                else:
                    spinmage = best_spinda.render_pattern()
                    prerendered[best_spinda.get_personality()] = spinmage
                
                img.paste(
                    spinmage,
                    (x * 25, y * 20),
                    spinmage
                )
                
                pids[y].append(best_spinda.get_personality())

        return (img, pids)

if __name__ == "__main__":
    from time import time
    (img, pids) = to_spindas("test/test_large.png", 100, 10)
    print(timeit("""to_spindas("test/test_large.png", 100, 10, invert=True)""", globals=vars(), number=10) / 10)
    img.resize((img.size[0]*10, img.size[1]*10), Image.Resampling.NEAREST)#.show()
    img.save("res/test_res.png")
    with open("res/test.json", "w") as f:
        json.dump(pids, f)