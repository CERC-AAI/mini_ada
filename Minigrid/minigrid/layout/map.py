import numpy as np
import pandas as pd
import random
import importlib
import re

from minigrid.layout.tiles import *

from minigrid.layout.constants import GENERATION_STATE
from mini_ada.scripts import utiles


class Map:

    def __init__(self, layout_map):
        self.map = layout_map
        self.height = len(layout_map)
        self.width = len(layout_map[0])
        self.obj_map = self.get_obj_map()

    def get_obj_map(self):
        obj_map = []
        for row_idx in range(len(self.map)):
            row = []
            for col_idx in range(len(self.map[0])):
                tile_str = self.map[row_idx][col_idx]
                tile_class, params = get_class_from_tile_str(tile_str)
                obj = None
                if tile_class is not None:
                    obj = tile_class(position=(row_idx, col_idx), params=params)
                    # if obj.tile_type == "ExitCorr":
                    # breakpoint()

                row.append(obj)
            obj_map.append(row)

        self.obj_map = obj_map

        return obj_map

    def get_exit_coords_list(self):
        _map = self.map
        exits = []
        for row_idx in range(len(_map)):
            for col_idx in range(len(_map[0])):
                # TODO: Handle Tile
                if _map[row_idx][col_idx] == "Exit":
                    exits.append((row_idx, col_idx))

        self.exit_coords_list = exits

        return exits

    def sync_map_using_obj_map(self):
        _map = []
        for row_idx in range(len(self.obj_map)):
            row = []
            for col_idx in range(len(self.obj_map[0])):
                obj = self.obj_map[row_idx][col_idx]

                if obj is None:
                    row.append(None)
                else:
                    row.append(obj.get_tile_str_repr())
            _map.append(row)

        self.map = _map

        return _map


# todo look at this class
class MasterMap(Map):
    def __init__(self, height=None, width=None, layout_map=None):
        if layout_map is None:
            layout_map = self._init_map(height, width)

        super().__init__(layout_map)

        self.exit_coords_list = self.get_exit_coords_list()

    def _init_map(self, height, width):
        # Init master_map
        _map = []

        for i in range(height):
            row = []
            for j in range(width):
                row.append(None)
            _map.append(row)

        return _map

    def init_submap_in_map(self, submap_obj):
        submap = submap_obj.obj_map

        mastermap_height = self.height
        mastermap_width = self.width

        submap_height = submap_obj.height
        submap_width = submap_obj.width

        # Randomly pick valid coordinate to place submap

        start_row_idx = random.randint(0, mastermap_height - submap_height)
        start_col_idx = random.randint(0, mastermap_width - submap_width)
        # Insert submap into mastermap
        for row_idx in range(submap_height):
            for col_idx in range(submap_width):
                map_row = row_idx + start_row_idx
                map_col = col_idx + start_col_idx
                if self.obj_map[map_row][map_col] is None:
                    self.obj_map[map_row][map_col] = submap[row_idx][col_idx]
                else:
                    raise ValueError(f"Map has already been initialized")

        self.sync_map_using_obj_map()

    def get_exit_coords_list(self):
        _map = self.map
        exits = []
        for row_idx in range(len(_map)):
            for col_idx in range(len(_map[0])):
                # TODO: Handle Tile
                if _map[row_idx][col_idx] != None:
                    if "Exit" in _map[row_idx][col_idx]:
                        exits.append((row_idx, col_idx))

        self.exit_coords_list = exits

        return exits

    def _can_merge(self, submap_obj, start_coords):
        _has_space = True

        submap = submap_obj.obj_map

        mastermap_height = self.height
        mastermap_width = self.width

        for r in range(len(submap)):
            for c in range(len(submap[0])):
                row_idx = start_coords[0] + r
                col_idx = start_coords[1] + c
                # todo add check that row_idx
                if (
                    row_idx < 0
                    or row_idx >= mastermap_height
                    or col_idx < 0
                    or col_idx >= mastermap_width
                ):
                    # breakpoint()
                    _has_space = False
                    break
                else:
                    mastermap_tile = self.obj_map[row_idx][col_idx]

                submap_tile = submap[r][c]

                if mastermap_tile is not None and not mastermap_tile.can_overlap_tile(
                    submap_tile
                ):  # todo check
                    _has_space = False
                    break
            if _has_space is False:
                break

        return _has_space

    def merge_maps(self, submap_obj, start_coords):
        submap = submap_obj.obj_map

        for r in range(len(submap)):
            for c in range(len(submap[0])):
                row_idx = start_coords[0] + r
                col_idx = start_coords[1] + c
                mastermap_tile = self.obj_map[row_idx][col_idx]
                submap_tile = submap[r][c]

                self.obj_map[row_idx][col_idx] = (
                    submap_tile
                    if mastermap_tile is None
                    else mastermap_tile.resolve_overlap(submap_tile)
                )

    def left_right_up_down_merge(self, submap_obj):
        submap = submap_obj.obj_map

        # directions = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]
        directions = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]

        mastermap_exits_coords_list = self.get_exit_coords_list()

        submap_exits_coords_list = submap_obj.get_exit_coords_list()
        # breakpoint()
        # print("mastermat EXITS:", mastermap_exits_coords_list)
        # print("submap EXITS:", submap_exits_coords_list)
        # breakpoint()
        has_merged = False

        # todo to shuffle the coordinates before doing for loops, done
        random.shuffle(mastermap_exits_coords_list)
        random.shuffle(submap_exits_coords_list)

        for mastermap_coords in mastermap_exits_coords_list:
            for submap_coords in submap_exits_coords_list:

                # Attempt overlap, left, right, up, down, merges wrt master map
                # for i, direction in enumerate(directions):
                # print(i, direction)
                start_coords = (
                    mastermap_coords[0] - submap_coords[0],
                    mastermap_coords[1] - submap_coords[1],
                )

                if self._can_merge(submap_obj, start_coords) is True:
                    # print("mergeable")
                    self.merge_maps(submap_obj, start_coords)
                    has_merged = True

                    mastermap_tile_r, mastermap_tile_c = (
                        mastermap_coords[0],
                        mastermap_coords[1],
                    )
                    submap_merge_tile_r, submap_merge_tile_c = (
                        mastermap_coords[0],
                        mastermap_coords[1],
                    )
                    mastermap_tile = self.obj_map[mastermap_tile_r][mastermap_tile_c]
                    submap_merge_tile = self.obj_map[submap_merge_tile_r][
                        submap_merge_tile_c
                    ]

                    # Update the mastermap_tile
                    if mastermap_tile is not None:
                        self.obj_map[mastermap_tile_r][mastermap_tile_c] = (
                            mastermap_tile.update(GENERATION_STATE.MERGE)
                        )

                    # Non-Overlapping merge: also need to update the submap tile
                    if (
                        mastermap_tile_r != submap_merge_tile_r
                        or mastermap_tile_c != submap_merge_tile_c
                    ):
                        if submap_merge_tile is not None:
                            self.obj_map[submap_merge_tile_r][submap_merge_tile_c] = (
                                submap_merge_tile.update(GENERATION_STATE.MERGE)
                            )

                    # print(f"Master coords: {mastermap_coords}, submap_coords: {submap_coords}, Successful start_coords: {start_coords}")
                    break
                if has_merged:
                    break
            if has_merged:
                break
        return has_merged

    def attempt_to_merge_maps(self, submap_obj, rotation=True):
        has_merged = False
        submap = submap_obj
        # Try rotating map up to 270 degrees

        # randomly rotate first
        randnum = np.random.randint(0, 4)
        for i in range(randnum):
            submap = SubMap.rotate(submap)

        num_rotations = 4 if rotation else 1  # todo, check if 4 instead of 3 works
        for i in range(num_rotations):
            has_merged = self.left_right_up_down_merge(submap)
            submap = SubMap.rotate(submap)
            if has_merged:
                self.sync_map_using_obj_map()
                break
        if not has_merged:
            # breakpoint()
            # print(f"No valid merge rotation found!")
            pass

        return has_merged

    def update_map_tiles(self, state: GENERATION_STATE):
        # Run each tile object's update function with a given state
        obj_map = self.obj_map
        for row_idx in range(len(obj_map)):
            for col_idx in range(len(obj_map[0])):
                tile = obj_map[row_idx][col_idx]
                if tile is not None:
                    obj_map[row_idx][col_idx] = tile.update(state=state)
                    if state == GENERATION_STATE.END:
                        if tile.tile_type == "Exit":
                            if (
                                tile.get_param() == "Corridor"
                                or tile.get_param() == "Room"
                            ):
                                obj_map[row_idx][col_idx] = Wall(
                                    position=(row_idx, col_idx)
                                )
                else:
                    # Turn all None tiles into Wall tiles if it is the end of all merging
                    obj_map[row_idx][col_idx] = (
                        Wall(position=(row_idx, col_idx))
                        if state == GENERATION_STATE.END
                        else None
                    )

        self.sync_map_using_obj_map()

    def to_csv(self, filepath):
        self.sync_map_using_obj_map()
        return pd.DataFrame(np.array(self.map)).to_csv(
            filepath, index=False, header=False
        )

    # 15/05/24 i added flag "map_generation_status" so that in case we want to save image of unfinished map we replace empty tiles i.e. ",,,,," in csv
    def to_npy(self, map_generation_status="finished") -> np.array:
        # self.sync_map_using_obj_map()
        # nparr = np.array(self.map)
        # nparr[nparr == "Space"] = 0  # constants, mappings, todo daria
        # nparr[nparr == "Wall"] = 1
        # nparr[nparr == "Undf(Wall)"] = 2
        # nparr[nparr == "Exit(Room)"] = 3
        # nparr[nparr == "Exit(Corridor)"] = 4
        # if (
        #    map_generation_status == "in_progress"
        # ):  # todo daria, maybe remove in the future
        #    nparr[nparr == None] = -1
        # nparr = nparr.astype(int)
        # return nparr

        # todo daria check that the function after modification works as before 21/05/2024
        breakpoint()
        self.sync_map_using_obj_map()
        nparr = np.array(self.map)

        nparr = utiles.convert_tiles(nparr)

        return nparr

    def saveas_numpy_arr(self, filepath: str) -> None:
        self.sync_map_using_obj_map()
        nparr = np.array(self.map)

        # np.save(
        #    "/network/scratch/d/daria.yasafova/miniada/numpy/string_arr.npy",
        #    nparr,
        # )
        # breakpoint()
        nparr[nparr == "Space"] = 0
        nparr[nparr == "Wall"] = 1
        nparr = nparr.astype(int)
        np.save(filepath, nparr)

    @classmethod
    def from_csv(cls, filepath):
        layout_map = pd.read_csv(filepath, header=None).to_numpy().tolist()
        return cls(layout_map)


# todo look at this class
class SubMap(Map):

    def __init__(self, layout_map, weight=None):
        super().__init__(layout_map)
        self.weight = weight
        self.exit_coords_list = self.get_exit_coords_list()

    def get_exit_coords_list(self):
        _map = self.map
        exits = []
        for row_idx in range(len(_map)):
            for col_idx in range(len(_map[0])):
                # TODO: Handle Tile
                if _map[row_idx][col_idx] != None:
                    if "Exit" in _map[row_idx][col_idx]:
                        exits.append((row_idx, col_idx))

        self.exit_coords_list = exits

        return exits

    @classmethod
    def rotate(cls, submap):
        new_map = np.rot90(np.array(submap.map)).tolist()
        return cls(new_map, weight=submap.weight)

    @classmethod
    def from_csv(cls, filepath, weight=None):
        layout_map = pd.read_csv(filepath, header=None).to_numpy().tolist()
        return cls(layout_map, weight=weight)
