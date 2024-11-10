from PIL import Image
from spindafy import SpindaConfig
# from random import choice, random, randint
# import multiprocessing, 
import numpy as np
# from itertools import repeat, starmap
# from scipy import signal
# from matplotlib import pyplot as plt

# from itertools import permutations

# import time

PREDEFINED = {
    "ALL_BLACK": 1097720040,
    "ALL_WHITE": 0xff200000
}


BLACK = 1
WHITE = -1
NEUTRAL = 0

XNEXT = 25
YNEXT = 20

SINGLE_COLOR_THRESH = 0

sp_mask = np.array(SpindaConfig.sprite_mask)[:, :, 3]
sp_base = np.asarray(SpindaConfig.sprite_base)[:, :, 3]
# sp_mask[np.pad(sp_base, ((YNEXT, 0), (0, 0)))[:64, :64] + np.pad(sp_base, ((0, 0), (XNEXT, 0)))[:64, :64] > 0] = 0
spots: list[np.ndarray] = [None] * 4
for i in range(4):
    spots[i] = np.asarray(SpindaConfig.spot_masks[i])[:, :, 3]
    spots[i] = -np.where(spots[i], WHITE, BLACK)

def fast_evo(si: np.ndarray):
    
    # Sprite mask crop: image.crop((17, 15, 52, 48))
    # Subimg size: width 35, height 33

    threshed = np.average(si, 2) > (int(np.min(si)) + int(np.max(si))) / 2

    # Check if all white or all black is best for this subimage
    white = SpindaConfig.from_personality(PREDEFINED["ALL_WHITE"])
    black = SpindaConfig.from_personality(PREDEFINED["ALL_BLACK"])
    
    if np.count_nonzero(threshed[sp_mask[15:-16, 17:-12] == 0]) <= SINGLE_COLOR_THRESH:
        return white
    elif np.count_nonzero(~threshed[sp_mask[15:-16, 17:-12] == 0]) <= SINGLE_COLOR_THRESH:
        return black
    
    spinda = SpindaConfig()
    for spot_index in range(4):

        best_pos = (0, 0)
        best_sim = 1e10
        for i in range(0, 16, 5):
            for j in range(0, 16, 5):
                spinda.spots[spot_index] = (i, j)
                sim = spinda.get_difference_single(si, spot_index)
                if sim < best_sim:
                    best_sim = sim
                    best_pos = (i, j)
        
        # radius = 1
        # width = best_pos[0] - radius, best_pos[0] + radius + 1
        # height = best_pos[1] - radius, best_pos[1] + radius + 1
        # for i in range(*width):
        #     for j in range(*height):
        #         if i == j == 0:
        #             continue
        #         spinda.spots[spot_index] = (i, j)
        #         sim = spinda.get_difference_single(si, spot_index)
        #         if sim < best_sim:
        #             best_sim = sim
        #             best_pos = (i, j)
                
        spinda.spots[spot_index] = best_pos

    return spinda


def evolve(target_img: Image.Image | np.ndarray, pop_size: int, n_gens: int, include: list | None = None) -> tuple[float, SpindaConfig]:
    if type(target_img) == Image.Image:
        target_img = target_img.convert('1')
        target_img = np.array(target_img)
    s = fast_evo(target_img)
    return (0, s)

def render_to_spinda(filename, pop, n_generations, include = []) -> Image:
    with Image.open(filename) as target:
        (_, best_spinda) = evolve(target.convert("RGB"), pop, n_generations)
        return (best_spinda.render_pattern(), best_spinda)

if __name__ == "__main__":
    # (img, best) = render_to_spinda("badapple/frame6476.png", 250, 25)
    # img.resize((1000, 1000), Image.Resampling.NEAREST).show()
    fast_evo(np.zeros((35, 33)))