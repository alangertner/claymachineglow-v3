#!/usr/bin/env python3
"""
Carefully extract the Canada Dry machine from the reference photo.
"""

from PIL import Image, ImageFilter, ImageDraw
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(SCRIPT_DIR, 'reference-machine.jpg')
OUT = os.path.join(SCRIPT_DIR, 'machine_cutout.png')


def extract():
    img = Image.open(REF)
    w, h = img.size
    print(f"Reference image: {w}x{h}")
    
    # Crop to just the machine area first
    # Being more aggressive with the top crop to avoid the reflective panel
    left, top, right, bottom = 430, 245, 700, 1060  # Start below the reflective top
    
    cropped = img.crop((left, top, right, bottom))
    cw, ch = cropped.size
    
    arr = np.array(cropped)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    
    # Create base rectangular mask
    mask = np.ones((ch, cw), dtype=np.uint8) * 255
    
    # Remove background colors
    # Blue curtain (visible on edges)
    blue_bg = (b > 130) & (b > g + 50) & (g < 120)
    
    # Red curtain
    red_bg = (r > 120) & (r > g + 40) & (r > b + 40) & (g < 120) & (b < 120)
    
    # Apply exclusions
    mask[blue_bg] = 0
    mask[red_bg] = 0
    
    # Also mask out the extreme edges where background shows
    # Left edge
    mask[:, :8] = 0
    # Right edge  
    mask[:, -8:] = 0
    
    # Create PIL mask
    mask_pil = Image.fromarray(mask)
    
    # Fill holes - for each row, fill between first and last non-zero
    mask_arr = np.array(mask_pil)
    for row_idx in range(ch):
        row = mask_arr[row_idx]
        nonzero = np.where(row > 128)[0]
        if len(nonzero) > 5:  # Need reasonable content
            first = nonzero[0]
            last = nonzero[-1]
            mask_arr[row_idx, first:last+1] = 255
    
    mask_pil = Image.fromarray(mask_arr)
    
    # Morphological cleanup
    mask_pil = mask_pil.filter(ImageFilter.MaxFilter(3))
    mask_pil = mask_pil.filter(ImageFilter.MinFilter(3))
    
    # Edge softening
    mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(1.5))
    
    # Create output
    result = cropped.convert('RGBA')
    result.putalpha(mask_pil)
    
    # Trim
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    
    result.save(OUT)
    print(f"Saved: {OUT}")
    print(f"Size: {result.size}")
    
    return result


if __name__ == '__main__':
    extract()
