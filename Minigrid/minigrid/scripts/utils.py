import numpy as np


def convert_tiles(layout: np.ndarray, map_generation_status="finished") -> np.ndarray:
    layout[layout == "Space"] = 0  # constants, mappings, todo daria
    layout[layout == "Wall"] = 1
    layout[layout == "Undf(Wall)"] = 2
    layout[layout == "Exit(Room)"] = 3
    layout[layout == "Exit(Corridor)"] = 4

    if map_generation_status == "in_progress":  # todo daria, maybe remove in the future
        layout[layout == None] = -1
    layout = layout.astype(int)

    return layout
