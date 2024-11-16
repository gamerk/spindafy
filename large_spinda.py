from PIL import Image
from spinda_optimizer import evolve, fast_evo
import json, PIL.ImageOps
import numpy as np
from timeit import timeit

# this is definitely not the best way of doing this!
def to_spindas(filename, pop, n_generations, invert = False, use_np=False):
    with Image.open(filename) as target:
        target = target.convert("1")
        target = target.resize((target.size[0] // 2, target.size[1] // 2), resample=Image.Resampling.NEAREST)
        if invert: target = PIL.ImageOps.invert(target)

        tarr = np.array(target)

        num_x = int((target.size[0]+10)/25)
        num_y = int((target.size[1]+13)/20)

        tarr = np.pad(tarr, ((0, num_y*20+33 - tarr.shape[0]), (0, num_x*25+35 - tarr.shape[1])))

        if not use_np:
            img = Image.new("RGBA", (39 + num_x * 25, 44 + num_y * 20))
        else:
            img = np.zeros(( 44 + num_y * 20, 39 + num_x * 25, 4), dtype=np.uint8)
        pids = [[0] * num_x for _ in range(num_y)]

        for y in range(num_y):
            for x in range(num_x):
                sub_target = tarr[y*20:y*20+33, x*25:x*25+35]
                (_, best_spinda) = evolve(sub_target, pop_size=0, n_gens=0)
                
                if not use_np:
                    spinmage = best_spinda.render_pattern()
                    img.paste(
                        spinmage,
                        (x * 25, y * 20),
                        spinmage
                    )
                else:
                    spinmage = best_spinda.render_pattern_arr()
                    spinmage_mask = spinmage[:, :, 3] > 0#np.repeat((spinmage[:, :, 3:] > 0), 4, axis=2)
                    img[y * 20:y * 20 + spinmage.shape[0], x * 25:x * 25 + spinmage.shape[1]][spinmage_mask] = spinmage[spinmage_mask]
                
                pids[y][x] = (best_spinda.get_personality())

        if use_np:
            return (Image.fromarray(img), pids)
        else:
            return (img, pids)
    
if __name__ == "__main__":
    from time import time
    (img, pids) = to_spindas("test/test_large.png", 100, 10, use_np=True)
    print(timeit("""to_spindas("test/test_large.png", 100, 10, use_np=True)""", globals=vars(), number=10) / 10)
    print(timeit("""to_spindas("test/test_large.png", 100, 10, use_np=False)""", globals=vars(), number=10) / 10)
    img.resize((img.size[0]*10, img.size[1]*10), Image.Resampling.NEAREST)#.show()
    img.save("res/test_res.png")
    with open("res/test.json", "w") as f:
        json.dump(pids, f)