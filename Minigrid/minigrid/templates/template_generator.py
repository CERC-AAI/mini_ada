from minigrid.layout.map import MasterMap, SubMap
from minigrid.layout.constants import GENERATION_STATE
from pathlib import Path

LAYOUT_PATH = Path(__file__).resolve().parent.parent  / 'templates/'

if __name__ == '__main__':
    # TODO: Make into CLI tool
    height = 40
    width = 40

    mmap = MasterMap(height=40, width=40)
    smap_7 = SubMap.from_csv(f"{LAYOUT_PATH}/layout_7.csv")
    smap_8 = SubMap.from_csv(f"{LAYOUT_PATH}/layout_8.csv")
    smap_5 = SubMap.from_csv(f"{LAYOUT_PATH}/layout_9.csv")

    mmap.init_submap_in_map(smap_7)
    # mmap.to_csv("test_layout.csv")

    mmap.attempt_to_merge_maps(smap_8, rotation=True)
    mmap.attempt_to_merge_maps(smap_8, rotation=True)
    mmap.update_map_tiles(state=GENERATION_STATE.END)
    mmap.to_csv(f"{LAYOUT_PATH}/master_layout.csv")
