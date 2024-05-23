from minigrid.layout.map import MasterMap, SubMap
from minigrid.layout.constants import GENERATION_STATE
from pathlib import Path
import json
from minigrid.templates.util import now
import os
import glob
from numpy.random import choice
import numpy as np
from minigrid.scripts.save_np_as_png import save_map_image


LAYOUT_PATH = Path(__file__).resolve().parent.parent / "templates/"


def append_log(log_path: str, text) -> None:
    with open(log_path, "a") as file:
        file.write(json.dumps(text))  # use `json.loads` to do the reverse
        file.write("\n")


def normalize_dict_values(dictionary: dict):
    sum_ = 0
    value_sum = sum(dictionary.values())
    for key in dictionary:
        dictionary[key] = dictionary[key] / value_sum
        sum_ = sum_ + dictionary[key]


# todo make it return a map

"""
takes a path to a config file, and returns a single master map
"""





def generate_mastermap(args: dict) -> MasterMap:
    # TODO: Make into CLI tool

    # todo to find the bug, set random seeds and then pdb it

    if args.root_folder == "__minigrid_folder__":
        args.root_folder = f"{Path(__file__).parent.parent.resolve()}"
    elif args.root_folder == "__miniada_folder__":
        args.root_folder = f"{Path(__file__).parent.parent.parent.parent.resolve()}"

    maps = (
        {}
    )  # maps is a dict with path: value, and it updates value on each entry of a map

    for i in args.layouts:
        # TODO turn each string path into Path
        # TODO make sure that directory paths ending with / and without are processed the same

        """
        print(i)
        print(os.path.isdir(i.path))
        print("starts with layout", i.path.startswith("layout"))
        """

        if i.value == 0:  # don't consider maps that have value 0
            continue

        full_path = f"{args.root_folder}/{i.path}"

        # breakpoint()
        print(full_path)
        assert os.path.exists(full_path), "Path doesn't exit, please change the path"
        file_list = []
        if os.path.isdir(
            full_path
        ):  # if path is a directory, we add each .csv file that starts with "layout" in its name
            if not full_path.endswith("/"):
                full_path = full_path + "/"  # todo , temporary solution
            file_list = glob.glob(f"{full_path}layout*.csv")

        elif os.path.isfile(full_path):
            file_path = full_path
            if file_path.endswith(".csv"):
                file_list = [file_path]

        temp_maps = dict.fromkeys(file_list, i.value)
        # add new maps ("path: value" pairs), and for existing maps update values
        maps.update(temp_maps)

        """
        print(maps)

        print(
            len(
                glob.glob(
                    "/home/mila/d/daria.yasafova/mini_ada/Minigrid/minigrid/templates/layout*.csv"
                )
            )
        )
        print("ends with .csv", full_path.endswith(".csv"))
        print(full_path)
        print(i.value)
        """

    """
    j = 0
    maps_sum = sum(maps.values())
    sum_ = 0
    
    for i in maps:
        # print(i)
        # print("old value:", maps[i])
        maps[i] = maps[i] / maps_sum
        # print("new value", maps[i])
        sum_ = sum_ + maps[i]
        j = j + 1
        # print(j)
        """
    normalize_dict_values(maps)

    mmap = MasterMap(height=args.map.height, width=args.map.height)

    timestamp = now()
    timestamp = timestamp.replace(":", "_")
    log_path = f"{LAYOUT_PATH}/log_{timestamp}.txt"

    final_coverage_ratio = 0

    if args.map.logic == "layout_count":
        # do sth

        number_of_items_to_pick = args.map.layout_count
        layouts = choice(
            list(maps.keys()), number_of_items_to_pick, p=list(maps.values())
        )
        smap_init = SubMap.from_csv(f"{layouts[0]}")
        mmap.init_submap_in_map(smap_init)

        ####
        for i in range(len(layouts)):
            full_layout_path = f"{layouts[i]}"
            if i != 0:
                smap = SubMap.from_csv(f"{layouts[i]}")
                mmap.attempt_to_merge_maps(smap, rotation=True)
            cur_mmap = np.array(mmap.sync_map_using_obj_map())
            cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap == None].size / cur_mmap.size
            # todo daria removed logs and intermediate master maps
            """
            append_log(log_path, f"map_{i}:{full_layout_path}")
            append_log(
                log_path,
                f"current_mmap_coverage_ratio (after adding the map above) : {cur_map_coverage_ratio}",
            )
            

            mmap.to_csv(
                f"{LAYOUT_PATH}/master_layout_{timestamp}.csv"
            )  # store the intermediate master map
            """

    elif args.map.logic == "coverage_ratio":
        layout = choice(list(maps.keys()), 1, p=list(maps.values()))[0]
        # breakpoint()
        smap_init = SubMap.from_csv(f"{layout}")
        mmap.init_submap_in_map(smap_init)
        ## append_log(log_path, f"map : {layout}")

        ########### repetitions are possible with the previous method
        cur_mmap = np.array(mmap.sync_map_using_obj_map())
        cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap == None].size / cur_mmap.size

        map_count = 0
        timeout = 0
        while cur_map_coverage_ratio < args.map.coverage_ratio:
            # print("cur_map_coverage_ratio:", cur_map_coverage_ratio)
            drawn_map_path = choice(list(maps.keys()), 1, p=list(maps.values()))[0]
            smap = SubMap.from_csv(drawn_map_path)

            if mmap.attempt_to_merge_maps(smap, rotation=True) == False:
                ##append_log(log_path, "hello daria")
                timeout = timeout + 1
                ## append_log(log_path, f"timeout {timeout}")
                if timeout == args.map.timeout:
                    # print("INFO: timeout has been reached.") # todo print
                    """
                    append_log(log_path, "game over. you've reached timeout.")
                    append_log(
                        log_path,
                        f"final master map coverage ratio is : {cur_map_coverage_ratio}",
                    )
                    """
                    break
            else:
                timeout = 0
            # print(timeout)
            cur_mmap = np.array(mmap.sync_map_using_obj_map())
            cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap == None].size / cur_mmap.size
            """
            append_log(log_path, f"map_{map_count}: {drawn_map_path}")
            append_log(
                log_path,
                f"current_mmap_coverage_ratio (after adding the map above) : {cur_map_coverage_ratio}",
            )
            mmap.to_csv(
                f"{LAYOUT_PATH}/master_layout_{timestamp}.csv"
            )  # store the intermediate master map
            """
            map_npy = mmap.to_npy(map_generation_status="in_progress") 
            save_map_image(
                map_npy,
                full_path=f"{LAYOUT_PATH}/master_layout_{timestamp}.png",
            )
            mmap.to_csv(
                f"{LAYOUT_PATH}/master_layout_{timestamp}.csv"
            )  # store the intermediate master map
            # breakpoint() todo
            map_count = map_count + 1

        ###########
        # print("INFO: reached map coverage:", cur_map_coverage_ratio) todo print
        # if cur_map_coverage_ratio < args.map.coverage_ratio - 0.1: # done commented
        #    print("INFO: desired coverage wasn't reached")
        final_coverage_ratio = cur_map_coverage_ratio

    # todo daria, this can be removed later
    mmap.update_map_tiles(state=GENERATION_STATE.END)
    save_map_image(
        mmap,
        map_generation_status="finished",
        full_path=f"{LAYOUT_PATH}/master_layout_{timestamp}_END.png",
    )
    breakpoint()
    # done, add timestamp to the name of the output file so that it doesn't overwrite
    # mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv")

    # save configuration as log
    # append_log(log_path, args) # todo daria removed logs

    return mmap, final_coverage_ratio
