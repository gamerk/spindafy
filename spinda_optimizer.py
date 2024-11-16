from PIL import Image
from spindafy import SpindaConfig
import numpy as np

PREDEFINED = {
    "ALL_BLACK": 1097720040,
    "ALL_WHITE": 0xff200000
}


BLACK = 1
WHITE = -1
NEUTRAL = 0

XNEXT = 25
YNEXT = 20

SINGLE_COLOR_THRESH = 20

sp_mask = np.array(SpindaConfig.sprite_mask)[15:-16, 17:-12, 3] == 0
sp_mask_nonzero = np.count_nonzero(sp_mask)
# sp_base = np.asarray(SpindaConfig.sprite_base)[:, :, 3]
spots: list[np.ndarray] = [None] * 4
for i in range(4):
    spots[i] = np.asarray(SpindaConfig.spot_masks[i])[:, :, 3]
    spots[i] = -np.where(spots[i], WHITE, BLACK)

white = SpindaConfig.from_personality(PREDEFINED["ALL_WHITE"])
black = SpindaConfig.from_personality(PREDEFINED["ALL_BLACK"])

test1_points = [(0, 0), (0, 15), (15, 0), (15, 15)]
test2_points = {p: [(x, y) for x in (p[0] - 7, p[0] + 7)
                           for y in (p[1] - 7, p[1] + 7)
                           if 0 <= x <= 15 and 0 <= y <= 15] 
                    for p in test1_points}

def fast_evo(si: np.ndarray):
    
    # Sprite mask crop: image.crop((17, 15, 52, 48))
    # Subimg size: width 35, height 33

    # Check if all white or all black is best for this subimage

    counter = si[sp_mask]

    count = np.count_nonzero(counter)
    count2 = counter.size - count
    # count2 = np.count_nonzero(~si[sp_mask])
    # print(count, count2, count + count2, si.size, sp_mask.size, si[sp_mask].size)
    # raise Exception()
    
    if count <= SINGLE_COLOR_THRESH:
        return white
    elif count2 <= SINGLE_COLOR_THRESH:
        return black
    
    spinda = SpindaConfig()
    for spot_index in range(4):

        best_pos = (0, 0)
        best_sim = 1e10
        for i, j in test1_points:
            spinda.spots[spot_index] = (i, j)
            sim = spinda.get_difference_single(si, spot_index)
            if sim < best_sim:
                best_sim = sim
                best_pos = (i, j)
        
        for i, j in test2_points[best_pos]:
            spinda.spots[spot_index] = (i, j)
            sim = spinda.get_difference_single(si, spot_index)
            if sim < best_sim:
                best_sim = sim
                best_pos = (i, j)
                
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