#!/usr/bin/env python3
"""
Composite the Canada Dry vending machine into scene images at weird positions.
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF_MACHINE = os.path.join(SCRIPT_DIR, 'reference-machine.jpg')
SCENES_DIR = os.path.join(SCRIPT_DIR, 'scenes')
MACHINE_CUTOUT = os.path.join(SCRIPT_DIR, 'machine_cutout.png')

# Target machine height in scene images (pixels)
MACHINE_HEIGHT = 165  # ~150-180 range, keeping it moderate

def extract_machine():
    """Extract the Canada Dry machine from the reference photo using color masking."""
    print("Extracting machine from reference photo...")
    
    img = Image.open(REF_MACHINE)
    img_array = np.array(img)
    
    # The machine is roughly in the center-right area of the image
    # Crop to just the machine region first (approximate bounds)
    h, w = img_array.shape[:2]
    
    # Machine is roughly at center, on a mat
    # Looking at the image: machine starts around x=430 and ends around x=700
    # Vertically from around y=200 to bottom
    left = 410
    right = 720
    top = 150
    bottom = h - 80
    
    # Crop
    cropped = img.crop((left, top, right, bottom))
    cropped_array = np.array(cropped)
    ch, cw = cropped_array.shape[:2]
    
    # Create mask based on green color (the machine body is green)
    # Also include the white diagonal stripe and details
    r, g, b = cropped_array[:,:,0], cropped_array[:,:,1], cropped_array[:,:,2]
    
    # Green machine body: more green than red, not too dark
    green_mask = (g > r - 20) & (g > 60) & (g < 200) & (b < g + 50)
    
    # White stripe: high values in all channels
    white_mask = (r > 200) & (g > 200) & (b > 200)
    
    # Gold/yellow logo area: high red and green, lower blue
    gold_mask = (r > 150) & (g > 120) & (b < 150) & (r > b + 50)
    
    # Red text area: high red
    red_mask = (r > 150) & (r > g + 30) & (r > b + 30)
    
    # Pink labels: pinkish colors
    pink_mask = (r > 180) & (g > 100) & (g < 180) & (b > 130)
    
    # Combine masks
    combined = green_mask | white_mask | gold_mask | red_mask | pink_mask
    
    # Also add a spatial constraint - create a rough bounding polygon
    # The machine has a rectangular shape, let's define it more precisely
    mask_img = Image.new('L', (cw, ch), 0)
    draw = ImageDraw.Draw(mask_img)
    
    # Draw a polygon roughly outlining the machine
    # Machine is roughly centered in our crop
    machine_left = 45
    machine_right = 265
    machine_top = 0
    machine_bottom = ch - 5
    
    # Rectangular outline with slight taper at top
    polygon = [
        (machine_left + 5, machine_top),  # top-left
        (machine_right - 5, machine_top),  # top-right
        (machine_right, machine_bottom),  # bottom-right
        (machine_left, machine_bottom),   # bottom-left
    ]
    draw.polygon(polygon, fill=255)
    
    spatial_mask = np.array(mask_img) > 0
    
    # Final mask: color-based AND spatial
    final_mask = combined & spatial_mask
    
    # Clean up with morphological operations (using PIL)
    mask_pil = Image.fromarray((final_mask * 255).astype(np.uint8))
    
    # Dilate slightly then erode to fill holes
    mask_pil = mask_pil.filter(ImageFilter.MaxFilter(3))
    mask_pil = mask_pil.filter(ImageFilter.MaxFilter(3))
    mask_pil = mask_pil.filter(ImageFilter.MinFilter(3))
    
    # Slight blur for softer edges
    mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(1))
    
    # Apply mask to create RGBA image
    result = cropped.copy()
    result.putalpha(mask_pil)
    
    # Crop to actual machine bounds (trim transparent)
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    
    result.save(MACHINE_CUTOUT)
    print(f"Saved machine cutout to {MACHINE_CUTOUT} ({result.size})")
    return result


def manual_extract_machine():
    """More manual extraction approach with better control."""
    print("Manual extraction of machine...")
    
    img = Image.open(REF_MACHINE)
    img_array = np.array(img)
    h, w = img_array.shape[:2]
    
    # More precise crop based on visual inspection
    # The machine appears to be roughly centered horizontally
    left = 415
    right = 715
    top = 180
    bottom = h - 60
    
    cropped = img.crop((left, top, right, bottom))
    cw, ch = cropped.size
    
    # Create a cleaner mask by flood-filling from edges (background)
    # and inverting
    cropped_array = np.array(cropped)
    r, g, b = cropped_array[:,:,0], cropped_array[:,:,1], cropped_array[:,:,2]
    
    # Background is blue/red striped curtain and dark floor
    # Blue curtain: high blue, moderate red, low green
    blue_bg = (b > 100) & (b > g + 30) & (r < b + 50) & (g < 80)
    
    # Red curtain: high red, low green and blue
    red_bg = (r > 100) & (r > g + 50) & (r > b + 50)
    
    # Dark floor/mat: all channels dark
    dark_bg = (r < 60) & (g < 60) & (b < 60)
    
    # Christmas tree (green but different tone than machine)
    tree_bg = (g > r + 20) & (g > 80) & (g < 150) & (b < 100)
    
    # Background mask
    bg_mask = blue_bg | red_bg | dark_bg
    
    # Machine mask is inverse, cleaned up
    machine_mask = ~bg_mask
    
    # Apply spatial bounding box
    mask_img = Image.new('L', (cw, ch), 0)
    draw = ImageDraw.Draw(mask_img)
    
    # Define tighter bounds for machine body
    m_left = 50
    m_right = 260
    m_top = 0
    m_bottom = ch
    
    draw.rectangle([m_left, m_top, m_right, m_bottom], fill=255)
    spatial_mask = np.array(mask_img) > 0
    
    # Combine
    final_mask = machine_mask & spatial_mask
    
    # Clean up
    mask_pil = Image.fromarray((final_mask * 255).astype(np.uint8))
    mask_pil = mask_pil.filter(ImageFilter.MaxFilter(5))
    mask_pil = mask_pil.filter(ImageFilter.MinFilter(3))
    mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(2))
    
    # Create RGBA
    result = cropped.copy().convert('RGBA')
    result.putalpha(mask_pil)
    
    # Trim
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    
    result.save(MACHINE_CUTOUT)
    print(f"Saved cutout: {result.size}")
    return result


def create_clean_machine_cutout():
    """Create a clean cutout by defining explicit bounds and using semi-automated masking."""
    print("Creating clean machine cutout...")
    
    img = Image.open(REF_MACHINE)
    
    # Precise crop coordinates (from visual inspection)
    # Machine body bounds in the original image
    left, top, right, bottom = 428, 195, 705, 1070
    
    cropped = img.crop((left, top, right, bottom))
    cw, ch = cropped.size
    cropped_array = np.array(cropped)
    
    # Create mask based on NOT being background
    r, g, b = cropped_array[:,:,0], cropped_array[:,:,1], cropped_array[:,:,2]
    
    # The machine itself has these characteristics:
    # - Green body (g > r, g between 80-180)
    # - White stripe (all channels > 180)
    # - Gold logo (r and g high, b lower)
    # - Red text (r > 180, g and b < 150)
    # - Pink labels (r > 180, g between 100-180, b > 120)
    # - Black details (all low)
    
    # Background has:
    # - Blue curtain (b > 150, b > g*2, r < 100)
    # - Red curtain (r > 150, r > g*2, r > b*2)
    
    # Detect background
    blue_curtain = (b > 140) & (b > g + 80) & (r < b) & (g < 100)
    red_curtain = (r > 130) & (r > g + 60) & (r > b + 60)
    
    background = blue_curtain | red_curtain
    
    # Machine is everything in the center that's not background
    # Create spatial gradient - center is more likely machine
    cy, cx = ch // 2, cw // 2
    y_coords, x_coords = np.mgrid[0:ch, 0:cw]
    
    # Distance from center (normalized)
    center_weight = 1.0 - np.sqrt(((x_coords - cx) / (cw/2))**2 * 0.5 + 
                                    ((y_coords - cy) / (ch/2))**2 * 0.1)
    center_weight = np.clip(center_weight, 0, 1)
    
    # Create column-based weighting (machine is in center columns)
    col_weight = np.zeros((ch, cw))
    col_weight[:, 30:250] = 1.0  # Main machine column region
    
    # Combine: not background AND in center region
    machine_mask = (~background) & (col_weight > 0.5)
    
    # Clean up the mask
    mask_pil = Image.fromarray((machine_mask * 255).astype(np.uint8))
    
    # Fill holes
    mask_pil = mask_pil.filter(ImageFilter.MaxFilter(5))
    mask_pil = mask_pil.filter(ImageFilter.MaxFilter(3))
    mask_pil = mask_pil.filter(ImageFilter.MinFilter(5))
    
    # Soften edges
    mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(1.5))
    
    # Create RGBA
    result = cropped.convert('RGBA')
    result.putalpha(mask_pil)
    
    # Trim transparent areas
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    
    result.save(MACHINE_CUTOUT)
    print(f"Cutout saved: {result.size}")
    return result


def load_or_create_machine():
    """Load existing cutout or create new one."""
    if os.path.exists(MACHINE_CUTOUT):
        print("Loading existing machine cutout...")
        return Image.open(MACHINE_CUTOUT)
    return create_clean_machine_cutout()


def adjust_machine_for_scene(machine, scene_brightness, scene_contrast=1.0, color_temp='neutral'):
    """Adjust machine colors/brightness to match scene lighting."""
    # Brightness adjustment
    enhancer = ImageEnhance.Brightness(machine)
    adjusted = enhancer.enhance(scene_brightness)
    
    # Contrast
    enhancer = ImageEnhance.Contrast(adjusted)
    adjusted = enhancer.enhance(scene_contrast)
    
    # Slight color adjustments based on scene
    if color_temp == 'warm':
        # Add warmth (golden hour, indoor lights)
        r, g, b, a = adjusted.split()
        r = r.point(lambda x: min(255, int(x * 1.05)))
        b = b.point(lambda x: int(x * 0.95))
        adjusted = Image.merge('RGBA', (r, g, b, a))
    elif color_temp == 'cool':
        # Cooler (night, fluorescent)
        r, g, b, a = adjusted.split()
        r = r.point(lambda x: int(x * 0.95))
        b = b.point(lambda x: min(255, int(x * 1.05)))
        adjusted = Image.merge('RGBA', (r, g, b, a))
    
    return adjusted


def add_shadow(machine, direction='right', opacity=0.3, blur=10):
    """Add a drop shadow to the machine."""
    # Create shadow
    shadow = Image.new('RGBA', machine.size, (0, 0, 0, 0))
    
    # Get alpha channel and use as shadow shape
    alpha = machine.split()[3]
    
    # Offset for direction
    offsets = {
        'right': (8, 5),
        'left': (-8, 5),
        'center': (0, 5),
    }
    dx, dy = offsets.get(direction, (5, 5))
    
    # Create shadow layer
    shadow_layer = Image.new('RGBA', (machine.width + abs(dx) * 2 + blur * 2, 
                                       machine.height + abs(dy) * 2 + blur * 2), (0, 0, 0, 0))
    
    # Paste shadow (black with alpha)
    shadow_alpha = alpha.point(lambda x: int(x * opacity))
    shadow_img = Image.new('RGBA', machine.size, (0, 0, 0, 255))
    shadow_img.putalpha(shadow_alpha)
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur))
    
    # Position shadow
    sx = blur + max(0, dx)
    sy = blur + max(0, dy)
    shadow_layer.paste(shadow_img, (sx + dx, sy + dy), shadow_img)
    
    # Position machine
    mx = blur + max(0, -dx)
    my = blur + max(0, -dy)
    shadow_layer.paste(machine, (mx, my), machine)
    
    return shadow_layer


def composite_machine_to_scene(scene_path, machine, position, machine_height, 
                                brightness=1.0, contrast=1.0, color_temp='neutral',
                                shadow_dir='right', shadow_opacity=0.25):
    """Composite machine onto a scene at given position."""
    scene = Image.open(scene_path).convert('RGBA')
    sw, sh = scene.size
    
    # Scale machine to target height
    scale = machine_height / machine.height
    new_w = int(machine.width * scale)
    new_h = int(machine.height * scale)
    scaled = machine.resize((new_w, new_h), Image.LANCZOS)
    
    # Adjust for scene lighting
    adjusted = adjust_machine_for_scene(scaled, brightness, contrast, color_temp)
    
    # Add shadow
    with_shadow = add_shadow(adjusted, shadow_dir, shadow_opacity)
    
    # Calculate paste position (position is center of machine)
    px, py = position  # These are fractions 0-1
    paste_x = int(px * sw - with_shadow.width // 2)
    paste_y = int(py * sh - with_shadow.height // 2)
    
    # Composite
    scene.paste(with_shadow, (paste_x, paste_y), with_shadow)
    
    # Convert back to RGB for JPEG
    rgb_scene = Image.new('RGB', scene.size, (0, 0, 0))
    rgb_scene.paste(scene, mask=scene.split()[3] if scene.mode == 'RGBA' else None)
    
    # Actually, just convert directly
    result = scene.convert('RGB')
    
    return result


# Scene configurations with WEIRD positions
# Format: (filename, x, y, height, brightness, contrast, color_temp, shadow_dir, shadow_opacity)
SCENE_CONFIGS = [
    # Scene 1: Kensington - put it on a SECOND FLOOR BALCONY (upper left)
    ('scene1.jpg', 0.08, 0.25, 90, 0.95, 1.0, 'warm', 'right', 0.2),
    
    # Scene 2: Nathan Phillips - at the VERY EDGE of reflecting pool, partially reflected
    ('scene2.jpg', 0.88, 0.72, 140, 0.85, 1.05, 'cool', 'left', 0.15),
    
    # Scene 3: Dundas Square - in a dark ALLEY ENTRANCE, barely visible
    ('scene3.jpg', 0.92, 0.45, 100, 0.65, 0.9, 'cool', 'left', 0.1),
    
    # Scene 4: St Lawrence Market - UP on the wooden counter, among market stalls
    ('scene4.jpg', 0.85, 0.70, 110, 0.9, 1.0, 'warm', 'left', 0.2),
    
    # Scene 5: High Park - DEEP in the trees, partially obscured by fog
    ('scene5.jpg', 0.78, 0.42, 120, 0.75, 0.95, 'neutral', 'left', 0.15),
    
    # Scene 6: Toronto Islands - FAR END of pier, almost silhouetted against water
    ('scene6.jpg', 0.12, 0.78, 95, 0.95, 1.0, 'warm', 'right', 0.2),
    
    # Scene 7: Chinatown - BEHIND the lanterns, partially hidden by a doorframe
    ('scene7.jpg', 0.88, 0.58, 130, 0.7, 1.0, 'warm', 'left', 0.15),
    
    # Scene 8: PATH - around a CORNER, only half visible
    ('scene8.jpg', 0.12, 0.52, 150, 0.85, 1.0, 'cool', 'right', 0.2),
    
    # Scene 9: Distillery - UP on the FIRE ESCAPE balcony (upper left area)
    ('scene9.jpg', 0.15, 0.32, 85, 0.85, 1.0, 'warm', 'right', 0.15),
    
    # Scene 10: Gardiner Museum - AMONG the art displays, behind glass
    ('scene10.jpg', 0.72, 0.58, 130, 0.9, 1.0, 'neutral', 'left', 0.1),
]


def get_base_scene_without_machine(scene_path):
    """
    Since scenes already have machines composited, we need to work with them.
    For now, we'll just load the scene as-is and place our machine in a NEW position
    that doesn't overlap with the existing one.
    """
    return Image.open(scene_path)


def main():
    """Main processing function."""
    print("=" * 50)
    print("Canada Dry Machine Compositor")
    print("=" * 50)
    
    # Load or create machine cutout
    machine = load_or_create_machine()
    print(f"Machine cutout size: {machine.size}")
    
    # Process each scene
    results = []
    for config in SCENE_CONFIGS:
        filename, x, y, height, bright, contrast, temp, shadow_dir, shadow_op = config
        scene_path = os.path.join(SCENES_DIR, filename)
        
        if not os.path.exists(scene_path):
            print(f"Warning: {scene_path} not found, skipping")
            continue
        
        print(f"\nProcessing {filename}...")
        print(f"  Position: ({x:.2f}, {y:.2f}), Height: {height}px")
        
        # Composite
        result = composite_machine_to_scene(
            scene_path, machine, (x, y), height,
            bright, contrast, temp, shadow_dir, shadow_op
        )
        
        # Save (overwrite original)
        result.save(scene_path, 'JPEG', quality=92)
        print(f"  Saved: {scene_path}")
        
        results.append((filename, x, y))
    
    # Output coordinates for index.html
    print("\n" + "=" * 50)
    print("SCENE COORDINATES FOR index.html:")
    print("=" * 50)
    for filename, x, y in results:
        scene_num = filename.replace('scene', '').replace('.jpg', '')
        print(f"  {{ img: 'scenes/scene{scene_num}.jpg', name: '...', x: {x:.2f}, y: {y:.2f} }},")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
