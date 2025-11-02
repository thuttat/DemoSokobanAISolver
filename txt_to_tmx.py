import xml.etree.ElementTree as ET
import os, sys

def make_csv_block(lines):
    
    result = []
    for i, row in enumerate(lines):
        joined = ",".join(row)
        if i < len(lines) - 1:
            result.append(joined + ",")
        else:
            result.append(joined)
    return "\n".join(result)

def make_tmx(map_lines, map_id, tile_size=32, out_dir="maps"):
    height = len(map_lines)
    width = max(len(line) for line in map_lines) if height > 0 else 0
    map_lines = [line.ljust(width) for line in map_lines]

    # root <map>
    root = ET.Element("map", {
        "version":"1.10",
        "tiledversion":"1.11.2",
        "orientation":"orthogonal",
        "renderorder":"right-down",
        "width":str(width),
        "height":str(height),
        "tilewidth":str(tile_size),
        "tileheight":str(tile_size),
        "infinite":"0",
        "nextlayerid":"11",
        "nextobjectid":"1"
    })

    
    ET.SubElement(root, "tileset", {"firstgid":"1","source":"grass.tsx"})
    ET.SubElement(root, "tileset", {"firstgid":"7","source":"wall.tsx"})
    ET.SubElement(root, "tileset", {"firstgid":"8","source":"charactor.tsx"})
    ET.SubElement(root, "tileset", {"firstgid":"9","source":"box.tsx"})
    ET.SubElement(root, "tileset", {"firstgid":"10","source":"star.tsx"})

    
    floor_layer = ET.SubElement(root, "layer", {"id":"1","name":"Floor","width":str(width),"height":str(height)})
    floor_rows = [["1" if c != "#" else "0" for c in row] for row in map_lines]
    ET.SubElement(floor_layer, "data", {"encoding":"csv"}).text = make_csv_block(floor_rows)

    
    wall_layer = ET.SubElement(root, "layer", {"id":"2","name":"Wall","width":str(width),"height":str(height)})
    wall_rows = [["7" if c == "#" else "0" for c in row] for row in map_lines]
    ET.SubElement(wall_layer, "data", {"encoding":"csv"}).text = make_csv_block(wall_rows)

    
    checkpoint_layer = ET.SubElement(root, "layer", {"id":"10","name":"Checkpoint","width":str(width),"height":str(height)})
    checkpoint_rows = [["10" if c in ('.','+','*') else "0" for c in row] for row in map_lines]
    ET.SubElement(checkpoint_layer, "data", {"encoding":"csv"}).text = make_csv_block(checkpoint_rows)

    
    player_group = ET.SubElement(root, "objectgroup", {"id":"8","name":"Player"})
    box_group = ET.SubElement(root, "objectgroup", {"id":"9","name":"Box"})

    obj_id = 1
    for y, row in enumerate(map_lines):
        for x, ch in enumerate(row):
            if ch in ('@', '+'):
                ET.SubElement(player_group, "object", {
                    "id": str(obj_id),
                    "name": "Player",
                    "gid": "8",
                    "x": str(x * tile_size),
                    "y": str((y + 1) * tile_size),
                    "width": str(tile_size),
                    "height": str(tile_size)
                })
                obj_id += 1
            if ch in ('$', '*'):
                ET.SubElement(box_group, "object", {
                    "id": str(obj_id),
                    "name": "Box",
                    "gid": "9",
                    "x": str(x * tile_size),
                    "y": str((y + 1) * tile_size),
                    "width": str(tile_size),
                    "height": str(tile_size)
                })
                obj_id += 1

    root.set("nextobjectid", str(max(1, obj_id)))

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"map_{map_id}.tmx")
    ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)
    print("Created:", out_path)

def batch_convert(txt_file, out_dir="maps"):
    with open(txt_file, 'r', encoding='utf-8') as f:
        raw_lines = f.read().splitlines()

    current_map = []
    map_id = None
    n = 0
    for line in raw_lines + ["; end"]:
        if line.strip().startswith(';'):
            if current_map and map_id is not None:
                make_tmx(current_map, map_id, out_dir=out_dir)
                n += 1
                current_map = []
            parts = line.strip().split()
            map_id = parts[1] if len(parts) >= 2 and parts[1].isdigit() else None
        else:
            if line != "":
                current_map.append(line.rstrip("\n"))
    print(f"Finished: created {n} maps in '{out_dir}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python txt_to_tmx.py dataset.txt maps")
        sys.exit(1)
    txt_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) >= 3 else "maps"
    batch_convert(txt_file, out_dir)
