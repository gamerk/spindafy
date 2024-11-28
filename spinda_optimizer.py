from PIL import Image
from spindafy import SpindaConfig
import numpy as np

PREDEFINED = {
    "ALL_BLACK": 1097720040,
    "ALL_WHITE": 0xff200000
}

cached = [8384767]


BLACK = 1
WHITE = -1
NEUTRAL = 0

XNEXT = 25
YNEXT = 20

SINGLE_COLOR_THRESH = 10
NUM_STEPS = 1

sp_mask = np.array(SpindaConfig.sprite_mask)[15:-16, 17:-12, 3] == 0
sp_mask_nonzero = np.count_nonzero(sp_mask)
# sp_base = np.asarray(SpindaConfig.sprite_base)[:, :, 3]
spots: list[np.ndarray] = [None] * 4
for i in range(4):
    spots[i] = np.asarray(SpindaConfig.spot_masks[i])[:, :, 3]
    spots[i] = -np.where(spots[i], WHITE, BLACK)

white = SpindaConfig.from_personality(PREDEFINED["ALL_WHITE"])
black = SpindaConfig.from_personality(PREDEFINED["ALL_BLACK"])

def fast_evo(si: np.ndarray):
    
    # Sprite mask crop: image.crop((17, 15, 52, 48))
    # Subimg size: width 35, height 33

    # Check if all white or all black is best for this subimage

    counter = si[sp_mask]

    count = np.count_nonzero(counter)
    count2 = counter.size - count
    
    if count <= SINGLE_COLOR_THRESH:
        return white
    elif count2 <= SINGLE_COLOR_THRESH:
        return black

    spinda = SpindaConfig()

    for spot_index in range(4):

        best_pos = (0, 0)
        best_sim = 1e10

        radius = 15
        
        for iter in range(2):
            low = max(best_pos[0] - radius, 0), max(best_pos[1] - radius, 0)
            high = min(best_pos[0] + radius, 15), min(best_pos[1] + radius, 15)
            for i in range(low[0], high[0] + 1, (high[0] - low[0]) // NUM_STEPS):
                for j in range(low[1], high[1] + 1, (high[1] - low[1]) // NUM_STEPS):
                    if (i, j) == best_pos and iter > 0:
                        continue
                    spinda.spots[spot_index] = (i, j)
                    sim = spinda.get_difference_single(si, spot_index)
                    if sim < best_sim:
                        best_sim = sim
                        best_pos = spinda.spots[spot_index]
            radius //= 2
                
        spinda.spots[spot_index] = best_pos
    
    return spinda


def evolve(target_img: Image.Image | np.ndarray, pop_size: int, n_gens: int, include: list | None = None) -> tuple[float, SpindaConfig]:
    if type(target_img) == Image.Image:
        target_img = target_img.convert('L')
        target_img = np.array(target_img) > 127
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