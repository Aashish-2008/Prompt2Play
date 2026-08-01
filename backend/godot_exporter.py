import io
import zipfile
import json
from pathlib import Path

# Try optional SVG->PNG conversion using cairosvg. If not installed, fall back to embedding SVG unchanged.
try:
    import cairosvg
    _HAS_CAIROSVG = True
except Exception:
    _HAS_CAIROSVG = False


def _safe(s):
    return str(s).replace('\r','')


def create_godot_zip(spec: dict) -> bytes:
    """Create an improved Godot project zip bytes mapped from spec.
    The zip will include:
      - project.godot
      - scenes/main.tscn (with placeholder nodes for entities)
      - scripts/main.gd and scripts/entity.gd
      - spec.json for provenance
      - embedded frontend assets (assets/*) when available
      - README.txt with notes

    If cairosvg is available, SVG assets are converted to PNG and included as assets/{name}.png for Godot compatibility.
    """
    title = spec.get('title') or 'Prompt2PlayGodot'
    player_color = spec.get('player_color', '#000000')
    enemy_color = spec.get('enemy_color', '#ff0000')
    instructions = spec.get('instructions', '')

    # Minimal project.godot (small stub)
    project_godot = f"""[application]
config/name="{_safe(title)}"
run/main_scene="res://scenes/main.tscn"
"""

    # Prepare entity list
    entities = spec.get('entities') or []

    # main.gd prints basic info and lists entities at startup
    main_gd = f"""extends Node2D

# Auto-generated main script from Prompt2Play
var project_title = "{_safe(title)}"
var player_color = "{player_color}"
var enemy_color = "{enemy_color}"
var instructions = "{_safe(instructions)}"

func _ready():
    print('Prompt2Play Godot project ready -', project_title)
    print('Instructions:', instructions)
    # Entities loaded from spec.json (if present) for developer reference
    # See res://spec.json
"""

    entity_gd = f"""extends Node2D

# Generic entity script (developer: replace with gameplay logic)
func _ready():
    pass
"""

    # We'll populate main_tscn after processing and possibly converting assets so we can reference textures as ext_resources
    main_tscn = None

    entity_gd = f"""extends Node2D

# Generic entity script (developer: replace with gameplay logic)
func _ready():
    pass
"""

    readme = f"""Prompt2Play Godot export

Title: {title}
Instructions: {instructions}

Contents:
- project.godot: Godot project file (tiny stub)
- scenes/main.tscn: main scene with placeholder nodes
- scripts/main.gd: startup script that prints spec metadata
- spec.json: the structured spec used to generate this project
- assets/: any embedded assets from the web UI (sprite.svg, audio stubs) when available

Notes:
- This exporter targets Godot 3.x text scene format (format=2) for maximum compatibility.
- Open this folder in Godot (3.x) and inspect scenes/scripts.
- Replace placeholder visuals and implement game logic in scripts/.
- The included spec.json is useful for mapping entity parameters to scene setup.
"""

    # prepare spec.json
    spec_json_text = json.dumps(spec, indent=2)

    # locate frontend assets (sprite.svg, audio stubs) relative to repository layout
    base_dir = Path(__file__).resolve().parents[1]
    assets_dir = base_dir / 'frontend' / 'assets'
    embedded_assets = []
    conversion_notes = []
    if assets_dir.exists() and assets_dir.is_dir():
        for p in assets_dir.iterdir():
            if p.is_file():
                try:
                    content = p.read_bytes()
                    embedded_assets.append((p.name, content))
                except Exception:
                    pass

    # Process embedded assets and perform multi-resolution SVG->PNG conversion when possible
    assets_to_write = []  # tuple(name, bytes)
    png_candidates = []   # list of png filenames (for texture mapping)
    sizes = [64, 128, 256]

    # add original embedded assets first
    for name, content in embedded_assets:
        assets_to_write.append((name, content))

    # convert SVGs into multiple PNG sizes if cairosvg is available
    for name, content in embedded_assets:
        if name.lower().endswith('.svg'):
            base = name.rsplit('.', 1)[0]
            if _HAS_CAIROSVG:
                for s in sizes:
                    try:
                        png_bytes = cairosvg.svg2png(bytestring=content, output_width=s, output_height=s)
                        png_name = f"{base}_{s}.png"
                        assets_to_write.append((png_name, png_bytes))
                        # mark the largest size as the preferred texture for mapping
                        if s == max(sizes):
                            png_candidates.append(png_name)
                        conversion_notes.append(f'Converted {name} -> {png_name}')
                    except Exception as e:
                        conversion_notes.append(f'Failed to convert {name} @{s}px: {e}')
            else:
                conversion_notes.append(f'cairosvg not available; skipped converting {name}')

    # Fallback: if no png candidates were created but there are SVGs, include their svg names as candidates
    if not png_candidates:
        for n, _ in embedded_assets:
            if n.lower().endswith('.svg'):
                png_candidates.append(n)
    # If still empty, png_candidates remains empty

    # Map entities to textures: try matching by name, else pick the first candidate
    entities = spec.get('entities') or []
    entity_texture_map = {}
    for i, e in enumerate(entities):
        hint = (e.get('name') or e.get('type') or f'entity_{i}').strip().lower().replace(' ', '_')
        chosen = None
        # find candidate that contains hint
        for pc in png_candidates:
            if hint in pc.lower():
                chosen = pc
                break
        if not chosen and png_candidates:
            chosen = png_candidates[0]
        entity_texture_map[i] = chosen

    # Build ext_resource list: script id=1, textures id starting at 2
    ext_resources = []
    ext_resources.append({'id': 1, 'path': 'res://scripts/main.gd', 'type': 'Script'})
    tex_id_map = {}  # filename -> ext_id
    next_id = 2

    # Prefer PNGs and register textures in ascending size order so largest gets the highest id
    # Collect png texture names and optional svg fallback
    png_names = [name for name, _ in assets_to_write if name.lower().endswith('.png')]
    svg_names = [name for name, _ in assets_to_write if name.lower().endswith('.svg')]

    def _png_size(name):
        # extract size from pattern base_64.png, base_128.png, etc.; fallback to 0
        m = None
        try:
            m = int(name.rsplit('_', 1)[-1].split('.png')[0])
        except Exception:
            m = 0
        return m

    # sort pngs by size ascending (small -> large)
    png_names_sorted = sorted(png_names, key=_png_size)

    # register pngs first
    for name in png_names_sorted:
        tex_path = f'res://assets/{name}'
        tex_id_map[name] = next_id
        ext_resources.append({'id': next_id, 'path': tex_path, 'type': 'Texture'})
        next_id += 1

    # register svgs only if no pngs are available or also include them as alternatives
    for name in svg_names:
        if name in tex_id_map:
            continue
        tex_path = f'res://assets/{name}'
        tex_id_map[name] = next_id
        ext_resources.append({'id': next_id, 'path': tex_path, 'type': 'Texture'})
        next_id += 1

    # Build main.tscn content with ext_resource declarations and Sprite nodes per entity
    header = """[gd_scene load_steps=2 format=2]

; Auto-generated main scene from Prompt2Play
"""
    # Add entity comment block
    entities_comment = json.dumps(entities, indent=2)
    header += "; Entities (for convenience):\n; " + entities_comment.replace('\n', '\n; ') + "\n\n"

    ext_lines = ''
    for r in ext_resources:
        ext_lines += f"[ext_resource path=\"{r['path']}\" type=\"{r['type']}\" id={r['id']}]\n"

    main_lines = header + ext_lines + '\n'
    # Main node
    main_lines += '[node name="Main" type="Node2D"]\n'
    main_lines += 'script = ExtResource( 1 )\n\n'

    # Add Sprite nodes for each entity that have a mapped texture
    for i, e in enumerate(entities):
        tex_name = entity_texture_map.get(i)
        if not tex_name:
            continue
        tex_id = tex_id_map.get(tex_name)
        if not tex_id:
            continue
        # simple grid positions
        col = i % 6
        row = i // 6
        x = 100 + col * 80
        y = 80 + row * 80
        safe_name = (e.get('name') or e.get('type') or f'entity_{i}').strip().replace(' ', '_')
        node_block = f"[node name=\"{safe_name}_{i}\" type=\"Sprite\" parent=\".\"]\ntexture = ExtResource({tex_id})\nposition = Vector2( {x}, {y} )\n\n"
        main_lines += node_block

    main_tscn = main_lines

    # Build zip in memory
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('project.godot', project_godot)
        z.writestr('scenes/main.tscn', main_tscn)
        z.writestr('scripts/main.gd', main_gd)
        z.writestr('scripts/entity.gd', entity_gd)
        z.writestr('spec.json', spec_json_text)

        # write assets collected
        for name, content in assets_to_write:
            z.writestr(f'assets/{name}', content)

        # README augmentation: list conversion notes if any
        if conversion_notes:
            notes = '\nConversion notes:\n' + '\n'.join(conversion_notes) + '\n'
            z.writestr('README_CONVERSION_NOTES.txt', notes)

        z.writestr('README.txt', readme)

    bio.seek(0)
    return bio.read()
