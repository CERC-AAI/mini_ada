from minigrid.layout.map import MasterMap, SubMap
from minigrid.layout.constants import STATE_END_MERGES

if __name__ == '__main__':
    # TODO: Make into CLI tool
    height = 40
    width = 40

    mmap = MasterMap(height=40, width=40)
    smap_7 = SubMap.from_csv("layout_7.csv")
    smap_8 = SubMap.from_csv("layout_8.csv")

    mmap.init_submap_in_map(smap_7)
    # mmap.to_csv("test_layout.csv")

    mmap.attempt_to_merge_maps(smap_8, rotation=True)
    mmap.update_map_tiles(state=STATE_END_MERGES)
    mmap.to_csv("master_layout.csv")
