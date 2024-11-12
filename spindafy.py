from PIL import Image, ImageChops, ImageDraw
from random import randint
import numpy as np
from timeit import timeit

class SpindaConfig:
    sprite_base = Image.open("res/spinda_base.png")
    sprite_mask = Image.open("res/spinda_mask.png")
    spot_masks = [
        Image.open("res/spots/spot_1.png"),
        Image.open("res/spots/spot_2.png"),
        Image.open("res/spots/spot_3.png"),
        Image.open("res/spots/spot_4.png")
    ]
    spot_offsets = [
        (8, 6),
        (32, 7),
        (14, 24),
        (26, 25)
    ]

    sprite_mask_color_arr = np.array(sprite_mask)

    sprite_mask_arr = np.array(sprite_mask)[:, :, 3]
    spot_masks_arr = [np.array(i)[:, :, 3] for i in spot_masks]

    def __init__(self):
        self.spots = [
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0)
        ]

    def __str__(self):
        return f"<SpindaConfig> {self.spots}"
    
    @staticmethod
    def from_personality(pers):
        self = SpindaConfig()
        self.spots[0] = (pers & 0x0000000f, (pers & 0x000000f0) >> 4)
        self.spots[1] = ((pers & 0x00000f00) >> 8, (pers & 0x0000f000) >> 12)
        self.spots[2] = ((pers & 0x000f0000) >> 16, (pers & 0x00f00000) >> 20)
        self.spots[3] = ((pers & 0x0f000000) >> 24, (pers & 0xf0000000) >> 28)
        return self
    
    @staticmethod
    def random():
        return SpindaConfig.from_personality(randint(0, 0x100000000))

    def get_personality(self):
        pers = 0x00000000
        for i, spot in enumerate(self.spots):
            pers = pers | (spot[0] << i*8) | (spot[1] << i*8+4)
        return pers

    def render_pattern_2(self, only_pattern = False, crop = False):
        # Prepare a result image with the same size as base and bg either black or transparent
        size = self.sprite_base.size
        img = Image.new('RGBA', size, (0, 0, 0, 255 if only_pattern else 0))

        # When wanting an actual spinda, start by pasting in the base sprite
        if not only_pattern:
            img.paste(self.sprite_base, (0, 0))

        for index in range(4):
            # Calculate the top-left coordinate for the spot image
            position = (self.spot_offsets[index][0] + self.spots[index][0],
                        self.spot_offsets[index][1] + self.spots[index][1])

            # Create a full-size image for the full spot at the desired position,
            #   as composite operation requires same-sized images
            spot_full = Image.new('RGBA', size, (0, 0, 0, 0))
            spot_full.paste(self.spot_masks[index], position, mask=self.spot_masks[index])

            # Create temporary mask by combining mask and spot mask
            temp_mask = Image.new('RGBA', size, (0, 0, 0, 0))
            temp_mask.paste(self.sprite_mask, (0, 0), mask=spot_full)

            if only_pattern:
                # Composite the white spot onto the masked area
                temp_mask = Image.composite(spot_full, temp_mask, temp_mask)

            # Composite the new mask with the current result
            img = Image.composite(temp_mask, img, temp_mask)

        if crop:
            img = img.crop((17, 15, 52, 48))

        return img
    
    def render_pattern_arr(self):
        base = np.array(self.sprite_base)

        for index in range(4):
            pos = (self.spot_offsets[index][1] + self.spots[index][1], 
                   self.spot_offsets[index][0] + self.spots[index][0])
            
            spot_arr = self.spot_masks_arr[index]
            sa_shape = (pos[0] + spot_arr.shape[0], pos[1] + spot_arr.shape[1])

            full_mask = np.logical_and(spot_arr, self.sprite_mask_color_arr[pos[0]:sa_shape[0], pos[1]:sa_shape[1], 3])

            base[pos[0]:sa_shape[0], pos[1]:sa_shape[1]][full_mask] = self.sprite_mask_color_arr[pos[0]:sa_shape[0], pos[1]:sa_shape[1]][full_mask]

            # subbase = base[pos[0]:sa_shape[0], pos[1]:sa_shape[1]]
            # full_mask = np.repeat(full_mask[...,None], 4, 2)
            # base[pos[0]:sa_shape[0], pos[1]:sa_shape[1]] = np.where(full_mask, self.sprite_mask_color_arr[pos[0]:sa_shape[0], pos[1]:sa_shape[1]], subbase)
        
        return base

    def render_pattern(self):
        
        result = Image.fromarray(self.render_pattern_arr())
    
        return result
        



    def get_difference_2(self, target):
        # Validate the mode will match the type used in the next step
        if target.mode != "RGB":
            target = target.convert("RGB")
        # Compare the resulting images by the total average pixel difference
        result = self.render_pattern(only_pattern=True, crop=True).convert("RGB")
        diff = ImageChops.difference(target, result)
        total_diff = 0
        for n, (r, g, b) in diff.getcolors():  # gives a list of counter and RGB values in the image
            total_diff += n*((r+g+b)/3)
        return total_diff
    
    def get_difference(self, target: Image.Image | np.ndarray):

        if type(target) == Image.Image:
            if target.mode != "RGB":
                target = target.convert("RGB")
            
            tarr = np.array(target)
        else:
            tarr = target

        base = np.zeros((64, 64), dtype=tarr.dtype)

        for index in range(4):
            pos = (self.spot_offsets[index][1] + self.spots[index][1], 
                   self.spot_offsets[index][0] + self.spots[index][0])
            
            spot_arr = self.spot_masks_arr[index]
            sa_shape = (pos[0] + spot_arr.shape[0], pos[1] + spot_arr.shape[1])

            base[pos[0]:sa_shape[0], pos[1]:sa_shape[1]] = spot_arr & self.sprite_mask_arr[pos[0]:sa_shape[0], pos[1]:sa_shape[1]]
        
        base = base[15:48, 17:52]
        base = np.repeat(base[..., None], 3, 2)


        diff = np.sum(np.abs(base - tarr))
        return diff
    
    def get_difference_single(self, tarr: np.ndarray, index: int):

        base = np.zeros((64, 64), dtype=tarr.dtype)

        pos = (self.spot_offsets[index][1] + self.spots[index][1], 
                self.spot_offsets[index][0] + self.spots[index][0])
        
        spot_arr = self.spot_masks_arr[index]
        sa_shape = (pos[0] + spot_arr.shape[0], pos[1] + spot_arr.shape[1])

        base[pos[0]:sa_shape[0], pos[1]:sa_shape[1]] = spot_arr & self.sprite_mask_arr[pos[0]:sa_shape[0], pos[1]:sa_shape[1]]
        
        base = base[15:48, 17:52]
        base = np.repeat(base[..., None], 3, 2)


        diff = np.sum(np.abs(base - tarr))
        return diff
            

if __name__ == "__main__":
    spin = SpindaConfig.from_personality(0x7a397866)
    print(timeit("""spin.render_pattern()""", globals=vars(), number=1000))
    print(timeit("""spin.render_pattern_2()""", globals=vars(), number=1000))
    print(timeit("""spin.get_difference_2(Image.new("RGB", (35, 33)))""", globals=vars(), number=1000))
    print(timeit("""spin.get_difference(Image.new("RGB", (35, 33)))""", globals=vars(), number=1000))
    #print(hex(spin.get_personality()))