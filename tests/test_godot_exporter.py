import io
import zipfile
import re
from backend import godot_exporter


def _list_zip_names(b):
    bio = io.BytesIO(b)
    with zipfile.ZipFile(bio) as z:
        return z.namelist()


def _read_zip_file(b, name):
    bio = io.BytesIO(b)
    with zipfile.ZipFile(bio) as z:
        return z.read(name).decode('utf-8')


def test_create_godot_zip_contains_scene_and_assets():
    spec = {
        'title': 'UnitTest Godot',
        'entities': [{'name': 'player', 'type': 'player'}, {'name': 'orb', 'type': 'collectible'}],
        'instructions': 'Test'
    }
    b = godot_exporter.create_godot_zip(spec)
    names = _list_zip_names(b)

    # required files
    assert 'project.godot' in names
    assert 'scenes/main.tscn' in names
    assert 'scripts/main.gd' in names
    assert 'spec.json' in names

    # assets: either converted PNGs or original SVG placeholder or both
    asset_pngs = [n for n in names if n.startswith('assets/') and n.lower().endswith('.png')]
    asset_svgs = [n for n in names if n.startswith('assets/') and n.lower().endswith('.svg')]

    # At minimum, either PNGs exist (if cairosvg present) or SVGs exist
    assert asset_pngs or asset_svgs

    # main.tscn should reference ExtResource entries and Sprite nodes
    main_txt = _read_zip_file(b, 'scenes/main.tscn')
    # ext_resource lines
    assert re.search(r"\[ext_resource .*id=1\]", main_txt)
    # main node with script extresource reference
    assert 'script = ExtResource( 1 )' in main_txt
    # there should be at least one Sprite node if any textures registered
    if asset_pngs or asset_svgs:
        assert re.search(r'type="Sprite"', main_txt) or re.search(r"\[node name=\".*\" type=\"Sprite\"", main_txt)
