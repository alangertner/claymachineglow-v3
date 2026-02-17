#!/usr/bin/env python3
"""
Final compositor - place Canada Dry machine in WEIRD positions in each scene.
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCENES_DIR = os.path.join(SCRIPT_DIR, 'scenes')
MACHINE_CUTOUT = os.path.join(SCRIPT_DIR, 'machine_cutout.png')


def add_shadow(machine, offset=(6, 4), opacity=0.3, blur=8):
    """Add realistic drop shadow."""
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1])) + 5
    canvas = Image.new('RGBA', 
                       (machine.width + pad * 2, machine.height + pad * 2), 
                       (0, 0, 0, 0))
    
    alpha = machine.split()[3]
    shadow_alpha = alpha.point(lambda x: int(x * opacity))
    shadow = Image.new('RGBA', machine.size, (0, 0, 0, 255))
    shadow.putalpha(shadow_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    
    sx = pad + offset[0]
    sy = pad + offset[1]
    canvas.paste(shadow, (sx, sy), shadow)
    
    mx = pad
    my = pad
    canvas.paste(machine, (mx, my), machine)
    
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    
    return canvas


def adjust_machine(machine, brightness=1.0, contrast=1.0, saturation=1.0, temperature='neutral'):
    """Adjust machine appearance for scene matching."""
    result = machine.copy()
    
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(result)
        result = enhancer.enhance(brightness)
    
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(contrast)
    
    if saturation != 1.0:
        enhancer = ImageEnhance.Color(result)
        result = enhancer.enhance(saturation)
    
    if temperature != 'neutral':
        r, g, b, a = result.split()
        if temperature == 'warm':
            r = r.point(lambda x: min(255, int(x * 1.06)))
            b = b.point(lambda x: int(x * 0.94))
        elif temperature == 'cool':
            r = r.point(lambda x: int(x * 0.94))
            b = b.point(lambda x: min(255, int(x * 1.06)))
        elif temperature == 'night':
            r = r.point(lambda x: int(x * 0.88))
            g = g.point(lambda x: int(x * 0.92))
            b = b.point(lambda x: min(255, int(x * 1.08)))
        result = Image.merge('RGBA', (r, g, b, a))
    
    return result


def composite_scene(scene_path, machine, config):
    """Composite machine into scene."""
    scene = Image.open(scene_path).convert('RGBA')
    sw, sh = scene.size
    
    # Scale machine
    scale = config['height'] / machine.height
    new_size = (int(machine.width * scale), int(machine.height * scale))
    scaled = machine.resize(new_size, Image.LANCZOS)
    
    # Adjust appearance
    adjusted = adjust_machine(
        scaled,
        config.get('brightness', 1.0),
        config.get('contrast', 1.0),
        config.get('saturation', 1.0),
        config.get('temperature', 'neutral')
    )
    
    # Add shadow
    shadow_cfg = config.get('shadow', {})
    with_shadow = add_shadow(
        adjusted,
        shadow_cfg.get('offset', (6, 4)),
        shadow_cfg.get('opacity', 0.25),
        shadow_cfg.get('blur', 8)
    )
    
    # Calculate position (x, y are CENTER of machine as fraction 0-1)
    x_frac = config['x']
    y_frac = config['y']
    paste_x = int(x_frac * sw - with_shadow.width // 2)
    paste_y = int(y_frac * sh - with_shadow.height // 2)
    
    # Clamp
    paste_x = max(0, min(sw - with_shadow.width, paste_x))
    paste_y = max(0, min(sh - with_shadow.height, paste_y))
    
    # Composite
    scene.paste(with_shadow, (paste_x, paste_y), with_shadow)
    
    return scene.convert('RGB')


# WEIRD POSITIONS for each scene
# The goal: physically possible but unexpected places
SCENE_CONFIGS = [
    # Scene 1: Kensington Market
    # WEIRD SPOT: Way down the street, barely visible in the distance
    {
        'file': 'scene1.jpg',
        'name': 'Kensington Market',
        'x': 0.88,  # Far right
        'y': 0.62,  # Mid-lower
        'height': 80,  # Small - appears far away
        'brightness': 0.85,
        'contrast': 0.95,
        'saturation': 0.9,
        'temperature': 'warm',
        'shadow': {'offset': (-4, 3), 'opacity': 0.2, 'blur': 5}
    },
    
    # Scene 2: Nathan Phillips Square
    # WEIRD SPOT: Almost off-screen left, by the pillars
    {
        'file': 'scene2.jpg',
        'name': 'Nathan Phillips Square',
        'x': 0.05,  # Far left edge
        'y': 0.68,  # Lower
        'height': 120,
        'brightness': 0.8,
        'contrast': 1.0,
        'saturation': 0.85,
        'temperature': 'cool',
        'shadow': {'offset': (5, 4), 'opacity': 0.15, 'blur': 7}
    },
    
    # Scene 3: Dundas Square (rainy night)
    # WEIRD SPOT: Reflected in the wet pavement, across the street
    {
        'file': 'scene3.jpg',
        'name': 'Dundas Square',
        'x': 0.75,  # Right side
        'y': 0.78,  # Low - on the wet street
        'height': 100,
        'brightness': 0.65,
        'contrast': 0.9,
        'saturation': 0.8,
        'temperature': 'night',
        'shadow': {'offset': (-3, 2), 'opacity': 0.1, 'blur': 6}
    },
    
    # Scene 4: St. Lawrence Market
    # WEIRD SPOT: Far back in the market, tiny, among the stalls
    {
        'file': 'scene4.jpg',
        'name': 'St. Lawrence Market',
        'x': 0.28,  # Left of center
        'y': 0.52,  # Upper-middle
        'height': 55,  # Very small - far in the distance
        'brightness': 0.75,
        'contrast': 0.9,
        'saturation': 0.85,
        'temperature': 'warm',
        'shadow': {'offset': (3, 2), 'opacity': 0.15, 'blur': 4}
    },
    
    # Scene 5: High Park (foggy autumn)
    # WEIRD SPOT: Almost hidden behind a tree trunk, far right
    {
        'file': 'scene5.jpg',
        'name': 'High Park',
        'x': 0.08,  # Far left
        'y': 0.65,  # Lower
        'height': 130,
        'brightness': 0.7,
        'contrast': 0.85,
        'saturation': 0.75,  # Muted by fog
        'temperature': 'neutral',
        'shadow': {'offset': (5, 4), 'opacity': 0.12, 'blur': 10}
    },
    
    # Scene 6: Toronto Islands
    # WEIRD SPOT: At the very end of the pier, nearly silhouetted
    {
        'file': 'scene6.jpg',
        'name': 'Toronto Islands',
        'x': 0.38,  # Center-left
        'y': 0.78,  # Low on pier
        'height': 95,
        'brightness': 0.9,
        'contrast': 1.0,
        'saturation': 0.9,
        'temperature': 'warm',
        'shadow': {'offset': (5, 3), 'opacity': 0.2, 'blur': 6}
    },
    
    # Scene 7: Chinatown Spadina
    # WEIRD SPOT: Way down the alley, past all the storefronts
    {
        'file': 'scene7.jpg',
        'name': 'Chinatown Spadina',
        'x': 0.48,  # Dead center
        'y': 0.85,  # Very low (far down the alley)
        'height': 50,  # Tiny - very far away
        'brightness': 0.55,
        'contrast': 0.85,
        'saturation': 0.7,
        'temperature': 'warm',
        'shadow': {'offset': (2, 2), 'opacity': 0.08, 'blur': 3}
    },
    
    # Scene 8: PATH Underground
    # WEIRD SPOT: Around the corner, partially hidden by pillar
    {
        'file': 'scene8.jpg',
        'name': 'PATH Underground',
        'x': 0.18,  # Left side
        'y': 0.58,  # Mid
        'height': 140,
        'brightness': 0.85,
        'contrast': 1.0,
        'saturation': 0.9,
        'temperature': 'cool',
        'shadow': {'offset': (6, 4), 'opacity': 0.18, 'blur': 8}
    },
    
    # Scene 9: Distillery District
    # WEIRD SPOT: Up on a balcony/fire escape (upper left)
    {
        'file': 'scene9.jpg',
        'name': 'Distillery District',
        'x': 0.12,  # Left
        'y': 0.38,  # Upper
        'height': 70,  # Smaller - up high
        'brightness': 0.75,
        'contrast': 0.95,
        'saturation': 0.85,
        'temperature': 'warm',
        'shadow': {'offset': (4, 3), 'opacity': 0.12, 'blur': 5}
    },
    
    # Scene 10: Gardiner Museum
    # WEIRD SPOT: Blending in with the art displays (behind glass)
    {
        'file': 'scene10.jpg',
        'name': 'Gardiner Museum',
        'x': 0.58,  # Right of center
        'y': 0.72,  # Lower
        'height': 90,
        'brightness': 0.88,
        'contrast': 0.95,
        'saturation': 0.9,
        'temperature': 'neutral',
        'shadow': {'offset': (3, 2), 'opacity': 0.1, 'blur': 5}
    },
]


def main():
    print("=" * 60)
    print("Canada Dry Machine - Weird Position Compositor")
    print("=" * 60)
    
    # Load machine
    if not os.path.exists(MACHINE_CUTOUT):
        print(f"Error: {MACHINE_CUTOUT} not found. Run extract_machine.py first.")
        return
    
    machine = Image.open(MACHINE_CUTOUT)
    print(f"Machine cutout: {machine.size}")
    
    results = []
    
    for cfg in SCENE_CONFIGS:
        scene_path = os.path.join(SCENES_DIR, cfg['file'])
        if not os.path.exists(scene_path):
            print(f"Warning: {scene_path} not found")
            continue
        
        print(f"\n{cfg['name']}:")
        print(f"  Position: ({cfg['x']:.2f}, {cfg['y']:.2f})")
        print(f"  Height: {cfg['height']}px")
        
        result = composite_scene(scene_path, machine, cfg)
        result.save(scene_path, 'JPEG', quality=92)
        print(f"  Saved: {cfg['file']}")
        
        results.append(cfg)
    
    # Output coordinates for index.html
    print("\n" + "=" * 60)
    print("UPDATE index.html with these SCENES coordinates:")
    print("=" * 60)
    print()
    print("const SCENES = [")
    for cfg in results:
        print(f"  {{ img: 'scenes/{cfg['file']}', name: '{cfg['name']}', x: {cfg['x']:.2f}, y: {cfg['y']:.2f} }},")
    print("];")
    
    print("\n✓ Done! All scenes composited.")


if __name__ == '__main__':
    main()
