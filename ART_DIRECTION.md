# Clay Machine Glow v3 — Art Direction

## Core Concept
**"The act of looking transforms what is seen"**

The images must serve this thesis. When desaturated, they should feel like memories — melancholic, contemplative, architectural. When color bleeds in around the machine, it should feel like awakening, like seeing for the first time. When the full scene saturates, it should feel like revelation.

## The Problem with v2
The current images are:
- Busy, playful, Where's Waldo-style cartoon illustrations
- Designed for a game, not art installation
- Too many competing focal points (crowds of tiny figures)
- Color feels arbitrary, not meaningful
- The machine is "hidden" cartoonishly, like an Easter egg
- They collapse into visual noise in greyscale

## v3 Visual Direction: "Cinematic Realism"

### Style
**Photorealistic digital painting** with a cinematic, almost film-still quality.

Think: 
- Gregory Crewdson's suburban uncanny
- Edward Hopper's solitude and light
- Vilhelm Hammershøi's quiet interiors (applied to exteriors)
- Contemporary urban photography with intentional composition

### Characteristics
1. **Atmospheric Depth** — Fog, haze, golden hour light, dusk. Environments that feel lived-in but uncrowded. Air you can feel.

2. **Deliberate Composition** — Each image composed like a film frame. Clear focal regions, leading lines, intentional negative space.

3. **Tonal Richness** — Rich shadows, luminous highlights. Images that work as tonal studies in greyscale, with color adding emotional depth rather than just "prettiness."

4. **Sparse Human Presence** — Few or no visible people. If present, they're distant, absorbed in their own world, backs turned. The viewer is alone.

5. **Natural Integration** — The ceramic vending machine sits naturally in the environment, like it belongs there. It's strange, yes, but it doesn't scream "find me!" — it waits.

### Color Philosophy
- **Saturated State**: Rich, immersive, emotional. Warm oranges and blues. Golden light. Deep shadows with color.
- **Desaturated State**: Silvery, contemplative, cinematic. The images should be BEAUTIFUL in greyscale — like classic black & white photography.
- **The Transition**: As color bleeds in around the machine, it should feel like life returning. The color is the reward for attention.

### The Machine
The ceramic vending machine should:
- Be visible but not obvious
- Placed in contextually appropriate locations (against a wall, near a corner, in a nook)
- Catch light in a way that makes it slightly luminous
- Feel like it could actually exist there
- Size: approximately human-scale (5-6 feet tall)
- Aesthetic: handmade ceramic, warm terracotta/cream tones, slightly weathered

## Scene-by-Scene Direction

### Scene 1: Kensington Market (x: 0.167, y: 0.454)
**Mood**: Late afternoon light filtering through vintage awnings
**Setting**: A quieter corner of Kensington — brick facades, eclectic storefronts, hanging plants
**Machine placement**: Left side, tucked against a brick wall between shops, partially shadowed
**Palette**: Warm brick reds, teal door paint, golden afternoon light

### Scene 2: Nathan Phillips Square (x: 0.738, y: 0.432)
**Mood**: Dusk, city lights beginning
**Setting**: The iconic arches reflected in the pool, City Hall rising behind
**Machine placement**: Right side, near the reflecting pool edge, catching the blue hour glow
**Palette**: Steel blues, warm window glows from buildings, purple-pink sky gradient

### Scene 3: Dundas Square (x: 0.302, y: 0.787)
**Mood**: Night, urban glow, rain-slicked streets
**Setting**: Neon and LED screens, but quieter — late night, few people
**Machine placement**: Lower left, against a building base, reflecting neon colors
**Palette**: Electric blues, magentas, warm yellows from signs, wet asphalt reflections

### Scene 4: St. Lawrence Market (x: 0.452, y: 0.866)
**Mood**: Early morning, soft light through industrial windows
**Setting**: Interior — the grand hall, stalls being set up, shafts of morning light
**Machine placement**: Lower center, among empty vendor stalls, catching a shaft of light
**Palette**: Warm wood browns, brass fixtures, cream morning light, pops of fruit color

### Scene 5: High Park (x: 0.364, y: 0.497)
**Mood**: Autumn fog, mysterious morning
**Setting**: A path through old trees, leaves carpeting the ground, mist rolling
**Machine placement**: Center-left, beside the path among the trees, fog-softened
**Palette**: Golden yellows and oranges of fall leaves, grey mist, green moss, brown bark

### Scene 6: Toronto Islands (x: 0.745, y: 0.803)
**Mood**: Golden hour, water light
**Setting**: The view back toward the city skyline, a quiet beach or pier
**Machine placement**: Right side, lower portion, on weathered wood of a pier or near shore
**Palette**: Blue water, golden sky, warm sand, cool city silhouette in background

### Scene 7: Chinatown Spadina (x: 0.254, y: 0.676)
**Mood**: Twilight, neon beginning to glow
**Setting**: Traditional signage, hanging lanterns, narrow street view
**Machine placement**: Left of center, beside a traditional shop entrance
**Palette**: Red lanterns, gold signage, jade greens, warm incandescent interior glows

### Scene 8: PATH Underground (x: 0.768, y: 0.361)
**Mood**: Liminal, fluorescent yet melancholic
**Setting**: The underground corridor after hours — empty, clean, slightly eerie
**Machine placement**: Right side, upper area, at a corridor junction
**Palette**: Fluorescent whites, corporate blues, occasional warm retail lighting

### Scene 9: Distillery District (x: 0.737, y: 0.675)
**Mood**: Golden evening, Victorian industrial romance
**Setting**: Cobblestone streets, preserved brick industrial buildings
**Machine placement**: Right of center, in a cobblestone alcove against aged brick
**Palette**: Warm brick reds and oranges, black iron details, golden string lights

### Scene 10: Gardiner Museum (x: 0.435, y: 0.366)
**Mood**: Contemplative, museum stillness
**Setting**: Interior or exterior of the Gardiner — glass, ceramics, clean modernism
**Machine placement**: Center-left, inside the museum among display cases, or outside against the facade
**Palette**: Museum whites, glass reflections, warm ceramic tones, cool museum lighting

## Technical Requirements

### Image Specifications
- Resolution: 1536x1024 pixels minimum (landscape)
- Format: PNG
- Aspect ratio: 3:2

### Machine Coordinates
The ceramic vending machine must be findable at approximately these normalized coordinates (x, y where 0,0 is top-left, 1,1 is bottom-right):

| Scene | Name | x | y |
|-------|------|---|---|
| 1 | Kensington Market | 0.167 | 0.454 |
| 2 | Nathan Phillips Square | 0.738 | 0.432 |
| 3 | Dundas Square | 0.302 | 0.787 |
| 4 | St. Lawrence Market | 0.452 | 0.866 |
| 5 | High Park | 0.364 | 0.497 |
| 6 | Toronto Islands | 0.745 | 0.803 |
| 7 | Chinatown Spadina | 0.254 | 0.676 |
| 8 | PATH Underground | 0.768 | 0.361 |
| 9 | Distillery District | 0.737 | 0.675 |
| 10 | Gardiner Museum | 0.435 | 0.366 |

### Hit Detection
- Hit radius: 180px at full scale
- Machine should occupy roughly 100-150px area at the coordinates
- Machine should be the ONLY ceramic/vending machine element in the scene

## Success Criteria

An image succeeds if:
1. It's beautiful in greyscale — you'd hang it on a wall
2. The color reveal feels like magic, not just a filter change
3. The machine is findable but not cartoonish
4. The atmosphere is immersive — you want to explore
5. It captures something true about that Toronto location
6. It serves the thesis: looking deeply transforms what you see

---

*v3 — February 2024*
