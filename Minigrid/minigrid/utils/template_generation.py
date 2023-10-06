import pandas as pd
import numpy as np
import random

from pathlib import Path

def get_exit_coords_list(_map):
    exits = []
    for row_idx in range(len(_map)):
        for col_idx in range(len(_map[0])):
            if _map[row_idx][col_idx] == 'Exit':
                exits.append((row_idx, col_idx))
    return exits

def has_space(mastermap, submap, start_coords):
    _has_space = True
    mastermap_height = len(mastermap)
    mastermap_width = len(mastermap[0])
    for r in range(len(submap)):
        for c in range(len(submap[0])):
            row_idx = start_coords[0]+r
            col_idx = start_coords[1]+c
            if row_idx < 0 or row_idx >= mastermap_height or col_idx < 0 or col_idx >= mastermap_width or mastermap[row_idx][col_idx] is not None:
                _has_space = False
                break
        if _has_space is False:
            break
            
    return _has_space

def merge_maps(mastermap, submap, start_coords):
    for r in range(len(submap)):
        for c in range(len(submap[0])):
            mastermap[start_coords[0]+r][start_coords[1]+c] = submap[r][c]

def left_right_up_down_merge(mastermap, submap):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    mastermap_exits_coords_list = get_exit_coords_list(mastermap)
    submap_exits_coords_list = get_exit_coords_list(submap)
    has_merged = False
    
    for mastermap_coords in mastermap_exits_coords_list:
        for submap_coords in submap_exits_coords_list:
            # Attempt left right up down merges wrt master map
            start_coords_list = [(mastermap_coords[0]-submap_coords[0], mastermap_coords[1]-1-submap_coords[1]), (mastermap_coords[0]-submap_coords[0], mastermap_coords[1]+1-submap_coords[1]), (mastermap_coords[0]-1-submap_coords[0], mastermap_coords[1]-submap_coords[1]), (mastermap_coords[0]+1-submap_coords[0], mastermap_coords[1]-submap_coords[1])]

            for i, start_coords in enumerate(start_coords_list):
                if has_space(mastermap, submap, start_coords) is True:
                    merge_maps(mastermap, submap, start_coords)
                    has_merged = True
                    # Convert joined Exits into Space
                    mastermap[mastermap_coords[0]][mastermap_coords[1]] = 'Space'
                    mastermap[mastermap_coords[0]+directions[i][0]][mastermap_coords[1]+directions[i][1]] = 'Space'
                    print(f"Master coords: {mastermap_coords}, submap_coords: {submap_coords}, Successful start_coords: {start_coords}, index {i}")
                    break
            if has_merged:
                break
        if has_merged:
            break
    return has_merged

def attempt_to_merge_maps(mastermap, submap, rotation=True):
    has_merged = False

    # Try rotating map up to 270 degrees
    num_rotations = 3 if rotation else 1
    for i in range(num_rotations):
        has_merged = left_right_up_down_merge(mastermap, submap)
        submap = np.rot90(np.array(submap)).tolist()
        if has_merged:
            break
    if not has_merged:
        print(f"No valid merge rotation found!")
    
    return has_merged

def generate_map_from_templates(layouts, map_save_path, map_height=40, map_width=40, layout_weights=None):
    master_map = []

    # Init master_map
    for i in range(map_height):
        row = []
        for j in range(map_width):
            row.append(None)
        master_map.append(row)
    
    master_map = np.array(master_map)
    mastermap_height = master_map.shape[0]
    mastermap_width = master_map.shape[1]

    indices = [i for i in range(len(layouts))]
    weights = np.array(layout_weights) if layout_weights is not None else np.array([1 for i in range(len(layouts))])
    probabilities = weights / np.sum(weights)
    # TODO: Handle different weights at different stages
    chosen_layout_indices = np.random.choice(indices, size=len(layouts), replace=False, p=probabilities)

    submap = layouts[chosen_layout_indices[0]]
    submap_height = submap.shape[0]
    submap_width = submap.shape[1]

    # Randomly pick valid coordinate to place submap
    start_row_idx = random.randint(0, mastermap_height-submap_height)
    start_col_idx = random.randint(0, mastermap_width-submap_width)

    # Insert submap into mastermap
    for row_idx in range(submap_height):
        for col_idx in range(submap_width):
            master_map[row_idx + start_row_idx][col_idx + start_col_idx] = submap[row_idx][col_idx]

    # Attempt to merge layouts into master map
    for i in range(1, len(chosen_layout_indices)):
        layout = layouts[chosen_layout_indices[i]]
        has_merged = attempt_to_merge_maps(master_map, layout, rotation=True)

    # Make all None or remaining Exits into Wall
    for row in range(len(master_map)):
        for col in range(len(master_map[0])):
            if master_map[row][col] is None or master_map[row][col] == 'Exit':
                master_map[row][col] = 'Wall'

    # Write master_map to CSV
    pd.DataFrame(np.array(master_map)).to_csv(map_save_path, index=False, header=False)

# TODO: Write function that takes in a template and generates a new template with random exits 

if __name__ == '__main__':
    TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates'
    MAP_SAVE_PATH = TEMPLATES_DIR / 'master_layout.csv'

    # Note : These layouts are for testing purposes
    layout_paths = [f"{TEMPLATES_DIR / 'layout_'}{i}.csv"for i in range(5, 8+1)]
    layouts = [pd.read_csv(path, header=None).to_numpy() for path in layout_paths]
    layout_weights = [0.1, 0.1, 0.25, 0.55]
    
    generate_map_from_templates(layouts, MAP_SAVE_PATH, map_height=40, map_width=40, layout_weights=layout_weights)