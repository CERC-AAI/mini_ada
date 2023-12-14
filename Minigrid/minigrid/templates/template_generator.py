from minigrid.layout.map import MasterMap, SubMap
from minigrid.layout.constants import GENERATION_STATE
from pathlib import Path
import yaml
import json
#from util import DotDict
from util import now
from minydra import MinyDict, resolved_args
import os
import glob
from pathlib import Path
from numpy.random import choice
import pandas as pd
import numpy as np

LAYOUT_PATH = Path(__file__).resolve().parent.parent  / 'templates/'

def append_log(log_path: str, text) -> None:
    with open(log_path, 'a') as file:
        file.write(json.dumps(text)) # use `json.loads` to do the reverse
        file.write('\n')

def find_config_defaults(dir_name: str) -> "list[Path]":
    """
    Returns a list of paths to config files:
    1. configs/{dir_name}/shared.yaml
    2. configs/{dir_name}/{$USER}.yaml if it exists

    Args:
        dir_name (str): The directory name to search for config files

    Returns:
        list[pathlib.Path]: a list of paths to config files inside dir_name
    """
    root = Path(__file__).parent.parent
    defaults = [root / "configs" / dir_name / "shared.yaml"]
    assert defaults[0].exists()
    user_conf = root / "configs" / dir_name / f"{os.environ['USER']}.yaml"
    if user_conf.exists():
        defaults.append(user_conf)
    return defaults


if __name__ == '__main__':
    # TODO: Make into CLI tool
    # todo to find the bug, set random seeds and then pdb it

    args = MinyDict.from_yaml("config.yaml")
    
    maps = {} # maps is a dict with path: value, and it updates value on each entry of a map

    for i in args.layout_connor:
        # TODO turn each string path into Path
        # TODO make sure that directory paths ending with / and without are processed the same
        
        assert os.path.exists(i.path)
        file_list = []
        if os.path.isdir(i.path): # if path is a directory, we add each .csv file that starts with "layout" in its name
            if not i.path.endswith('/'):
                i.path = i.path + '/' # todo , temporary solution
            file_list = glob.glob(f"{i.path}layout*.csv")
            
        elif os.path.isfile(i.path):
            
            file_path = i.path

            if file_path.endswith('.csv'):
                file_list = [file_path]
        
        temp_maps = dict.fromkeys(file_list, i.value)
        maps.update(temp_maps)
        
    j = 0
    maps_sum = sum(maps.values())
    sum = 0
    for i in maps:
        print(i)
        print('old value:', maps[i])
        maps[i]=maps[i]/maps_sum
        print('new value', maps[i])
        sum = sum + maps[i]
        j = j+1
        print(j)


    mmap = MasterMap(height=args.map.height, width=args.map.width)

    timestamp = now()
    log_path = f'{LAYOUT_PATH}/log_{timestamp}.txt'
    
    args.pretty_print()


    if args.map.logic=="layout_count":
        # do sth

        number_of_items_to_pick = args.map.layout_count
        layouts = choice(list(maps.keys()), number_of_items_to_pick, p=list(maps.values()))
        smap_init = SubMap.from_csv(f"{layouts[0]}")
        mmap.init_submap_in_map(smap_init)
       
        for i in range(len(layouts)):
            full_layout_path = f'{layouts[i]}'
            if i != 0:
                smap = SubMap.from_csv(f"{layouts[i]}")
                mmap.attempt_to_merge_maps(smap, rotation=True)
            cur_mmap = np.array(mmap.sync_map_using_obj_map())
            cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap==None].size/cur_mmap.size
            append_log(log_path, f'map_{i}:{full_layout_path}')
            append_log(log_path, f'current_mmap_coverage_ratio (after adding the map above) : {cur_map_coverage_ratio}')
            mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv") # store the intermediate master map


    elif args.map.logic == "coverage_ratio":
        layout = choice(list(maps.keys()), 1, p=list(maps.values()))[0]
        breakpoint()
        smap_init = SubMap.from_csv(f"{layout}")
        mmap.init_submap_in_map(smap_init)
        append_log(log_path, f'map : {layout}')
        
        ########### repetitions are possible with the previous method
        cur_mmap = np.array(mmap.sync_map_using_obj_map())
        cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap==None].size/cur_mmap.size

        map_count = 0
        timeout = 0
        while cur_map_coverage_ratio < args.map.coverage_ratio:
            print("cur_map_coverage_ratio:", cur_map_coverage_ratio)
            drawn_map_path = choice(list(maps.keys()), 1, p=list(maps.values()))[0]
            smap = SubMap.from_csv(drawn_map_path)
            
            if mmap.attempt_to_merge_maps(smap, rotation=True) == False:
                append_log(log_path, "hello daria")
                timeout = timeout + 1
                append_log(log_path, f'timeout {timeout}')
                if timeout == args.map.timeout:
                    print('game over')
                    append_log(log_path, "game over. you've reached timeout.")
                    append_log(log_path, f'final master map coverage ratio is : {cur_map_coverage_ratio}')
                    break
            else:
                timeout = 0
                
            cur_mmap = np.array(mmap.sync_map_using_obj_map())
            cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap==None].size/cur_mmap.size
            append_log(log_path, f'map_{map_count}: {drawn_map_path}')
            append_log(log_path, f'current_mmap_coverage_ratio (after adding the map above) : {cur_map_coverage_ratio}')
            mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv") # store the intermediate master map
            map_count = map_count + 1

    mmap.update_map_tiles(state=GENERATION_STATE.END)

    # done, add timestamp to the name of the output file so that it doesn't overwrite
    mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv")

    append_log(log_path, args)