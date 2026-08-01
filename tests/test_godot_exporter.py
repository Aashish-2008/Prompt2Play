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

    # If PNGs were created, prefer the largest PNG for sprite textures
    if asset_pngs:
        # parse ext_resource id -> path mapping
        id_to_path = {}
        for m in re.finditer(r'\[ext_resource path="(?P<path>[^"]+)" type="(?P<type>[^"]+)" id=(?P<id>\d+)\]', main_txt):
            id_to_path[int(m.group('id'))] = m.group('path')
        # find sprite texture usages (ExtResource(ids))
        sprite_ids = [int(x) for x in re.findall(r'texture = ExtResource\((\d+)\)', main_txt)]
        assert sprite_ids
        # largest png name ends with _256.png if available; derive candidate path
        largest_png = None
        for n in asset_pngs:
            if n.endswith('_256.png'):
                largest_png = f'res://{n}' if n.startswith('assets/') else f'res://assets/{n}'
                break
        # normalize id_to_path values to compare
        if largest_png:
            # map paths in id_to_path may include res://assets/...
            assert any(p.endswith('_256.png') for p in id_to_path.values())
            # check that at least one sprite references the ext_resource id that points to the largest png
            largest_ids = [i for i, p in id_to_path.items() if p.endswith('_256.png')]
            assert any(sid in largest_ids for sid in sprite_ids)
