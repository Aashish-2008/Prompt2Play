import io
import zipfile
from pathlib import Path


def _safe(s):
    return str(s).replace('\r','')


def create_godot_zip(spec: dict) -> bytes:
    """Create a minimal Godot project zip bytes mapped from spec.
    The zip contains project.godot, scenes/main.tscn, scripts/main.gd and a small README.
    """
    title = spec.get('title') or 'Prompt2PlayGodot'
    player_color = spec.get('player_color', '#000000')
    enemy_color = spec.get('enemy_color', '#ff0000')
    instructions = spec.get('instructions', '')

    # Minimal project.godot (very small, acceptable as a stub)
    project_godot = f"""[application]
config/name="{_safe(title)}"
run/main_scene="res://scenes/main.tscn"
"""

    # Minimal main.tscn - Node2D with script
    main_tscn = f"""[gd_scene load_steps=2 format=2]

[node name="Main" type="Node2D"]
script = ExtResource( 1 )

[node name="Hole" parent="." instance=ExtResource( 2 )]
position = Vector2( 400, 300 )
"""

    # Scripts
    main_gd = f"""extends Node2D

# Auto-generated main scene script from Prompt2Play
var player_color = "{player_color}"
var enemy_color = "{enemy_color}"
var instructions = "{_safe(instructions)}"

func _ready():
    print('Prompt2Play Godot stub ready. Title: { _safe(title) }')
"""

    hole_gd = f"""extends Area2D

# Hole logic stub: grow on eat
var area = 100.0

func swallow(amount):
    area += amount
    # In a real project, update scale/visuals here
"""

    readme = f"""Prompt2Play Godot export

Title: {title}
Instructions: {instructions}

This zip is a minimal stub. To make it a working Godot project:
- Open in Godot 3.x/4.x and migrate as needed
- Implement the node visuals and signals in scripts/main.gd and scripts/hole.gd
- Replace stub assets with real PNG/SVG sprites and sounds
"""

    # Build zip in memory
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('project.godot', project_godot)
        z.writestr('scenes/main.tscn', main_tscn)
        z.writestr('scripts/main.gd', main_gd)
        z.writestr('scripts/hole.gd', hole_gd)
        z.writestr('README.txt', readme)
    bio.seek(0)
    return bio.read()
