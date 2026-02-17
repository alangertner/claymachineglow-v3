#!/usr/bin/env python3
"""
Improved Canada Dry machine compositor with better extraction and positioning.
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF_MACHINE = os.path.join(SCRIPT_DIR, 'reference-machine.jpg')
SCENES_DIR = os.path.join(SCRIPT_DIR, 'scenes')
MACHINE_CUTOUT = os.path.join(SCRIPT_DIR, 'machine_cutout_v2.png')


def extract_machine_v2():
    """Better extraction with tighter masking."""
    print("Extracting machine (v2)...")
    
    img = Image.open(REF_MACHINE)
    
    # Very precise crop - just the machine body, no extras
    # Machine boundaries observed: left edge ~430, right ~700, top ~200, bottom ~1065
    left, top, right, bottom = 432, 205, 698, 1060
    
    cropped = img.crop((left, top, right, bottom))
    cw, ch = cropped.size
    arr = np.array(cropped)
    
    # Create mask by detecting what IS the machine (not what isn't)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    
    # Machine components:
    # 1. Green body - the most distinctive part
    #    The Canada Dry green is a specific teal-green
    green_body = (g > 80) & (g < 200) & (g > r - 30) & (g > b - 30) & (b > 60) & (b < 200)
    
    # 2. White diagonal stripe - bright area
    white_stripe = (r > 190) & (g > 190) & (b > 190)
    
    # 3. Gold/yellow logo  
    gold_logo = (r > 160) & (g > 130) & (g < 200) & (b < 120) & (r > b + 40)
    
    # 4. Red "CANADA DRY" text
    red_text = (r > 160) & (r > g + 50) & (r > b + 50)
    
    # 5. Pink flavor labels
    pink_labels = (r > 200) & (g > 130) & (g < 200) & (b > 150)
    
    # 6. Dark areas (coin slot, dispenser, edges)
    dark_parts = (r < 80) & (g < 80) & (b < 80)
    
    # 7. Gray/metallic parts
    gray_parts = (abs(r.astype(int) - g.astype(int)) < 30) & \
                 (abs(g.astype(int) - b.astype(int)) < 30) & \
                 (r > 80) & (r < 200)
    
    # Combine machine parts
    machine_color = green_body | white_stripe | gold_logo | red_text | pink_labels | dark_parts | gray_parts
    
    # Create spatial mask - rectangular with slight padding
    # The machine occupies roughly columns 20-250 in our crop
    spatial = np.zeros((ch, cw), dtype=bool)
    spatial[:, 15:252] = True
    
    # Combined mask
    combined = machine_color & spatial
    
    # Fill holes by finding the largest connected component region
    # For simplicity, let's use morphological operations
    mask_img = Image.fromarray((combined * 255).astype(np.uint8))
    
    # Heavy dilation to connect components
    for _ in range(3):
        mask_img = mask_img.filter(ImageFilter.MaxFilter(5))
    
    # Erosion to restore size
    for _ in range(2):
        mask_img = mask_img.filter(ImageFilter.MinFilter(5))
    
    # Fill any remaining holes by doing a flood fill from edges
    mask_arr = np.array(mask_img)
    
    # Create a filled version: anything enclosed by the mask edges
    # Find rows where there's machine content
    row_has_content = np.any(mask_arr > 128, axis=1)
    col_has_content = np.any(mask_arr > 128, axis=0)
    
    # For each row, fill between leftmost and rightmost content
    filled = np.zeros_like(mask_arr)
    for row_idx in range(ch):
        if row_has_content[row_idx]:
            row = mask_arr[row_idx]
            nonzero = np.where(row > 128)[0]
            if len(nonzero) > 0:
                left_edge = nonzero[0]
                right_edge = nonzero[-1]
                filled[row_idx, left_edge:right_edge+1] = 255
    
    # Use this filled mask
    mask_img = Image.fromarray(filled)
    
    # Slight Gaussian blur for edge softening
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(1.5))
    
    # Create RGBA result
    result = cropped.convert('RGBA')
    result.putalpha(mask_img)
    
    # Trim transparent areas
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    
    result.save(MACHINE_CUTOUT)
    print(f"Saved: {MACHINE_CUTOUT} ({result.size})")
    return result


def add_shadow(machine, offset=(6, 4), opacity=0.3, blur=8):
    """Add drop shadow with offset."""
    # Create larger canvas for shadow
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1]))
    canvas = Image.new('RGBA', 
                       (machine.width + pad * 2, machine.height + pad * 2), 
                       (0, 0, 0, 0))
    
    # Get alpha for shadow shape
    alpha = machine.split()[3]
    
    # Create shadow
    shadow_alpha = alpha.point(lambda x: int(x * opacity))
    shadow = Image.new('RGBA', machine.size, (0, 0, 0, 255))
    shadow.putalpha(shadow_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    
    # Position shadow
    sx = pad + offset[0]
    sy = pad + offset[1]
    canvas.paste(shadow, (sx, sy), shadow)
    
    # Position machine
    mx = pad
    my = pad
    canvas.paste(machine, (mx, my), machine)
    
    # Trim
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    
    return canvas


def adjust_brightness_contrast(img, brightness=1.0, contrast=1.0):
    """Adjust image brightness and contrast."""
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    return img


def apply_color_cast(img, temperature='neutral'):
    """Apply color temperature adjustment."""
    if temperature == 'neutral':
        return img
    
    r, g, b, a = img.split()
    
    if temperature == 'warm':
        r = r.point(lambda x: min(255, int(x * 1.08)))
        b = b.point(lambda x: int(x * 0.92))
    elif temperature == 'cool':
        r = r.point(lambda x: int(x * 0.92))
        b = b.point(lambda x: min(255, int(x * 1.08)))
    elif temperature == 'night':
        r = r.point(lambda x: int(x * 0.85))
        g = g.point(lambda x: int(x * 0.9))
        b = b.point(lambda x: min(255, int(x * 1.1)))
    
    return Image.merge('RGBA', (r, g, b, a))


def composite(scene_path, machine, x_frac, y_frac, height_px, 
              brightness=1.0, contrast=1.0, temperature='neutral',
              shadow_offset=(6, 4), shadow_opacity=0.25, shadow_blur=8):
    """Composite machine into scene."""
    
    scene = Image.open(scene_path).convert('RGBA')
    sw, sh = scene.size
    
    # Scale machine
    scale = height_px / machine.height
    new_size = (int(machine.width * scale), int(machine.height * scale))
    scaled = machine.resize(new_size, Image.LANCZOS)
    
    # Adjust appearance
    adjusted = adjust_brightness_contrast(scaled, brightness, contrast)
    adjusted = apply_color_cast(adjusted, temperature)
    
    # Add shadow
    with_shadow = add_shadow(adjusted, shadow_offset, shadow_opacity, shadow_blur)
    
    # Calculate position (x_frac, y_frac are center points)
    paste_x = int(x_frac * sw - with_shadow.width // 2)
    paste_y = int(y_frac * sh - with_shadow.height // 2)
    
    # Clamp to scene bounds
    paste_x = max(0, min(sw - with_shadow.width, paste_x))
    paste_y = max(0, min(sh - with_shadow.height, paste_y))
    
    # Composite
    scene.paste(with_shadow, (paste_x, paste_y), with_shadow)
    
    return scene.convert('RGB')


# Scene configurations: WEIRDER positions that are still physically possible
# The key is places you wouldn't normally look
SCENES = [
    # Scene 1: Kensington - DEEP in the shadowed doorway on left
    {
        'file': 'scene1.jpg',
        'x': 0.05, 'y': 0.55,  # Far left in the dark doorway
        'height': 160,
        'brightness': 0.7,  # Darker to match shadow
        'contrast': 0.95,
        'temperature': 'warm',
        'shadow_offset': (4, 3),
        'shadow_opacity': 0.15,  # Less shadow in shadow
    },
    
    # Scene 2: Nathan Phillips - RIGHT EDGE of the pool, barely in frame
    {
        'file': 'scene2.jpg',
        'x': 0.95, 'y': 0.75,  # Far right edge
        'height': 120,
        'brightness': 0.75,
        'contrast': 1.0,
        'temperature': 'cool',
        'shadow_offset': (-5, 3),
        'shadow_opacity': 0.2,
    },
    
    # Scene 3: Dundas Square - BEHIND the ceramic thing, in the window reflection
    {
        'file': 'scene3.jpg',
        'x': 0.06, 'y': 0.42,  # In the window reflection area
        'height': 100,
        'brightness': 0.6,
        'contrast': 0.9,
        'temperature': 'night',
        'shadow_offset': (3, 2),
        'shadow_opacity': 0.1,
    },
    
    # Scene 4: St Lawrence - FAR BACK, small, among the stalls
    {
        'file': 'scene4.jpg',
        'x': 0.15, 'y': 0.62,  # Back left area
        'height': 80,  # Smaller - it's far away
        'brightness': 0.85,
        'contrast': 0.95,
        'temperature': 'warm',
        'shadow_offset': (5, 4),
        'shadow_opacity': 0.2,
    },
    
    # Scene 5: High Park - FAR RIGHT behind the large tree trunk
    {
        'file': 'scene5.jpg',
        'x': 0.92, 'y': 0.55,  # Behind/beside the big tree
        'height': 140,
        'brightness': 0.7,
        'contrast': 0.9,
        'temperature': 'neutral',
        'shadow_offset': (-4, 3),
        'shadow_opacity': 0.15,
    },
    
    # Scene 6: Toronto Islands - FAR LEFT end of the pier
    {
        'file': 'scene6.jpg',
        'x': 0.08, 'y': 0.82,  # Left edge of pier
        'height': 100,
        'brightness': 0.95,
        'contrast': 1.0,
        'temperature': 'warm',
        'shadow_offset': (5, 4),
        'shadow_opacity': 0.25,
    },
    
    # Scene 7: Chinatown - DEEP in the alley, past the storefronts
    {
        'file': 'scene7.jpg',
        'x': 0.55, 'y': 0.72,  # Down the middle of the alley, small
        'height': 70,  # Very small - far away
        'brightness': 0.6,
        'contrast': 0.95,
        'temperature': 'warm',
        'shadow_offset': (2, 2),
        'shadow_opacity': 0.1,
    },
    
    # Scene 8: PATH - TUCKED by the pillar
    {
        'file': 'scene8.jpg',
        'x': 0.46, 'y': 0.58,  # By the central pillar
        'height': 150,
        'brightness': 0.9,
        'contrast': 1.0,
        'temperature': 'cool',
        'shadow_offset': (6, 4),
        'shadow_opacity': 0.2,
    },
    
    # Scene 9: Distillery - IN THE ARCHWAY, partially hidden
    {
        'file': 'scene9.jpg',
        'x': 0.72, 'y': 0.65,  # In the archway
        'height': 140,
        'brightness': 0.7,
        'contrast': 0.95,
        'temperature': 'warm',
        'shadow_offset': (-3, 3),
        'shadow_opacity': 0.15,
    },
    
    # Scene 10: Gardiner Museum - AMONG the displays behind glass
    {
        'file': 'scene10.jpg',
        'x': 0.38, 'y': 0.68,  # Among the display area
        'height': 100,
        'brightness': 0.85,
        'contrast': 0.95,
        'temperature': 'neutral',
        'shadow_offset': (3, 3),
        'shadow_opacity': 0.1,
    },
]


def main():
    print("=" * 60)
    print("Canada Dry Machine Compositor v2 - Weirder Positions")
    print("=" * 60)
    
    # Extract machine
    if os.path.exists(MACHINE_CUTOUT):
        print(f"Using existing cutout: {MACHINE_CUTOUT}")
        machine = Image.open(MACHINE_CUTOUT)
    else:
        machine = extract_machine_v2()
    
    print(f"Machine size: {machine.size}")
    
    # Need to restore original scenes first if they have the old composites
    # For now, we'll composite on top (the new positions shouldn't overlap old ones much)
    
    results = []
    
    for cfg in SCENES:
        scene_path = os.path.join(SCENES_DIR, cfg['file'])
        if not os.path.exists(scene_path):
            print(f"Warning: {scene_path} not found")
            continue
        
        print(f"\nProcessing {cfg['file']}...")
        print(f"  Position: ({cfg['x']:.2f}, {cfg['y']:.2f}), Height: {cfg['height']}px")
        
        result = composite(
            scene_path, machine,
            cfg['x'], cfg['y'], cfg['height'],
            cfg.get('brightness', 1.0),
            cfg.get('contrast', 1.0),
            cfg.get('temperature', 'neutral'),
            cfg.get('shadow_offset', (6, 4)),
            cfg.get('shadow_opacity', 0.25),
            cfg.get('shadow_blur', 8)
        )
        
        result.save(scene_path, 'JPEG', quality=92)
        print(f"  Saved: {scene_path}")
        
        results.append((cfg['file'], cfg['x'], cfg['y']))
    
    # Print coordinates for index.html
    print("\n" + "=" * 60)
    print("UPDATE index.html SCENES array with these coordinates:")
    print("=" * 60)
    print()
    print("const SCENES = [")
    for filename, x, y in results:
        scene_num = int(filename.replace('scene', '').replace('.jpg', ''))
        names = [
            'Kensington Market', 'Nathan Phillips Square', 'Dundas Square',
            'St. Lawrence Market', 'High Park', 'Toronto Islands',
            'Chinatown Spadina', 'PATH Underground', 'Distillery District',
            'Gardiner Museum'
        ]
        print(f"  {{ img: 'scenes/scene{scene_num}.jpg', name: '{names[scene_num-1]}', x: {x:.2f}, y: {y:.2f} }},")
    print("];")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
