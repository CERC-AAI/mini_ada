# "this .py file is a backup"

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
from minigrid.layout.map import Map

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
    height = 40
    width = 40
    # todo to find the bug, set random seeds and then pdb it
    with open('config.yaml') as config_file:
        config_dict = yaml.safe_load(config_file)
    #config = DotDict(config_dict)
    args = resolved_args()
    args = MinyDict.from_yaml("config.yaml")
    
    maps = {} # maps is a dict with path: value, and it updates value on each entry of a map
    ##path_list = []

    """
    breakpoint()
    #https://www.programiz.com/python-programming/methods/dictionary/update
    marks = {'Physics':67, 'Maths':87}
    internal_marks = {'Practical':48, 'Maths': 0}
    marks.update(internal_marks)
    print(marks)

    # Output: {'Physics': 67, 'Maths': 87, 'Practical': 48}
    """

    for i in args.layout_connor:
        # TODO turn each string path into Path
        # TODO make sure that directory paths ending with / and without are processed the same
        print(i)
        #breakpoint()
        #ith_path = Path(i.path)
        print(os. path. isdir(i.path))

        print('starts with layout', i.path.startswith('layout'))
        
        assert os.path.exists(i.path)
        file_list = []
        if os.path.isdir(i.path): # if path is a directory, we add each .csv file that starts with "layout" in its name
            if not i.path.endswith('/'):
                i.path = i.path + '/' # todo , temporary solution
            file_list = glob.glob(f"{i.path}layout*.csv")
            ##path_list.append(file_list)

            ##temp_maps = dict.fromkeys(file_list, i.value)
            # add new maps ("path: value" pairs), and for existing maps update values
            ##maps.update(temp_maps)
        elif os.path.isfile(i.path):
            #breakpoint()
            file_path = i.path
#            if file_path.startswith('layout') and file_path.endswith('.csv')
            if file_path.endswith('.csv'):
                file_list = [file_path]

            print('hi daria')

        ##path_list.append(file_list)

        temp_maps = dict.fromkeys(file_list, i.value)
        # add new maps ("path: value" pairs), and for existing maps update values
        maps.update(temp_maps)
        print(maps)
        #breakpoint()

        print(len(glob.glob("/home/mila/d/daria.yasafova/mini_ada/Minigrid/minigrid/templates/layout*.csv")))
        print("ends with .csv", i.path.endswith('.csv'))
        print(i.path)
        print(i.value)
    #breakpoint()

    #for i, j in maps:
    #    print(i)
    #    print(j)
    j = 0
    print('helllllooo')
    
    ### breakpoint()
    maps_sum = sum(maps.values())
    #breakpoint()
    sum = 0
    for i in maps:
        print(i)
        print('old value:', maps[i])
        maps[i]=maps[i]/maps_sum
        print('new value', maps[i])
        sum = sum + maps[i]
        j = j+1
        print(j)

    ### breakpoint()

#    if args.map.logic=="layout_count":
#        # do sth
 #   elif args.map.logic == "coverage_ratio":
        # do sth else


    number_of_items_to_pick = 10 # todo, move to config or use another logic

    # questions, do we want repetitions?
    # how important is the "map filling" logic? can we drop it and instead go with the idea of increasing the master map for our needs? i.e. the user asks how many maps we want to merge and dance from there?
    #layouts = choice(list(maps.keys()), number_of_items_to_pick, p=list(maps.values())) # replaced this with the next, correction A
    layout = choice(list(maps.keys()), 1, p=list(maps.values()))[0]
    breakpoint()

    #####
    # get a list of maps here by processing the map paths provided in the config.yaml file



    #####

    #mmap = MasterMap(height=config_dict['map']['height'], width=config_dict['map']['width']) # todo make height and width changable
    mmap = MasterMap(height=args.map.height, width=args.map.width)
    # todo what other parameters do we want?
    # todo randomly choose say 3 maps from LAYOUT_PATH
    # todo choose maps until the master map is full
    # todo given a set of maps, fill the master map with them until it's full
    # todo think of the condition of fullness
    # or todo fill the master map until 50/60/70 percent of the map is full

    # done changed logic
    
    # daria replaced this with layouts drawn by random weighted choice
    layouts_old = ['layouts_minigrid - layout_3_new_2.csv', 'layouts_minigrid - layout_4_new_5.csv', 'layouts_minigrid - layout_4_new_4.csv']
    ##smap_init = SubMap.from_csv(f"{LAYOUT_PATH}/{layouts[0]}")
    #smap_init = SubMap.from_csv(f"{layouts[0]}") replaced with the following line , correction A related
    smap_init = SubMap.from_csv(f"{layout}")
    mmap.init_submap_in_map(smap_init)
    import pandas as pd
    import numpy as np

    breakpoint()

    ## here to the for loop
    ########### repetitions are possible with the previous method
    cur_mmap = np.array(mmap.sync_map_using_obj_map())
    #drawn_map_path = choice(list(maps.keys()), 1, p=list(maps.values()))[0] # works, use in the loop


    timestamp = now()
    log_path = f'{LAYOUT_PATH}/log_{timestamp}.txt'
    append_log(log_path, f'map : {layout}') # move up TODO

    cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap==None].size/cur_mmap.size
    while cur_map_coverage_ratio < args.map.coverage_ratio:
        print("cur_map_coverage_ratio:", cur_map_coverage_ratio)
        drawn_map_path = choice(list(maps.keys()), 1, p=list(maps.values()))[0]
        smap = SubMap.from_csv(drawn_map_path)
#        mmap.attempt_to_merge_maps(smap, rotation=True)
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
        append_log(log_path, f'map : {drawn_map_path}')
        #breakpoint()
        mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv")

    mmap.update_map_tiles(state=GENERATION_STATE.END)

    # done, add timestamp to the name of the output file so that it doesn't overwrite
    mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv")

    # save configuration as log
    append_log(log_path, config_dict)
    ###########

    breakpoint()
    #mastermap = pd.DataFrame(np.array(mmap))
    

    timestamp = now()
    log_path = f'{LAYOUT_PATH}/log_{timestamp}.txt'
    ###breakpoint()
    for i in range(len(layouts)):
        # full_layout_path = f'{LAYOUT_PATH}/{layouts[i]}'
        full_layout_path = f'{layouts[i]}'
        if i != 0:
            # smap = SubMap.from_csv(f"{LAYOUT_PATH}/{layouts[i]}")
            try:
                smap = SubMap.from_csv(f"{layouts[i]}")
            except:
                breakpoint()
            mmap.attempt_to_merge_maps(smap, rotation=True)
            
        
        append_log(log_path, f'map_{i}:{full_layout_path}')
    ###breakpoint()
    mmap.update_map_tiles(state=GENERATION_STATE.END)
    breakpoint() 
    """
    smap_7 = SubMap.from_csv(f"{LAYOUT_PATH}/layouts_minigrid - layout_3_new_2.csv")
    smap_8 = SubMap.from_csv(f"{LAYOUT_PATH}/layouts_minigrid - layout_4_new_5.csv")
    #smap_8 = SubMap.from_csv(f"{LAYOUT_PATH}/layouts_minigrid - layout_3_new_4.csv")
    smap_5 = SubMap.from_csv(f"{LAYOUT_PATH}/layouts_minigrid - layout_4_new_4.csv")

    mmap.init_submap_in_map(smap_7)
    # mmap.to_csv("test_layout.csv")

    mmap.attempt_to_merge_maps(smap_8, rotation=True)
    mmap.attempt_to_merge_maps(smap_5, rotation=True)
    mmap.update_map_tiles(state=GENERATION_STATE.END)
    """



    # done, add timestamp to the name of the output file so that it doesn't overwrite
    mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv")

    

    # save configuration as log
    append_log(log_path, config_dict)
#    with open(f'{LAYOUT_PATH}/config_{timestamp}.txt', 'w') as file:
#        file.write(json.dumps(config_dict)) # use `json.loads` to do the reverse
#        file.write('\n')
#        file.write(json.dumps(config_dict))

    # todo, why it's weird? the master map output mis-generates maps 
    # todo, use black
    # todo, set a check to not allow the _has_space running infinitely
    # todo, to provide maps make the following options available:
    #   1. if user provides a str that is a folder, the program (searches for layouts and tries to parse/access them) takes all layouts in the folder
    #   2. if user provides a str that is a csv file the program tries to read as a layout
    #   3. if a map is repeated the score is updated according to the last occurance
    #   4. values are any numbers but then they're normalized in the code
    

    """
    layouts:
 - file:
    - path:
    - weight:
  - file_2:
    - path

layouts: [{file: [{path: ...}, {weight: ...}]}]

layouts:
 - file: [path_1]
     weight: 1
 - file: [path_2]
     weight: 2

layouts:
  path_1: 0.1
  path_2: 0.2
layouts: [{map_path_1:weight_1}, {map_path_2:weight_2},....]

    
    """

    # https://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
    # one list of files and one list of weights and i pass it to the weighted random choice
    # overwrite weights of repetitions
    # future work: generate a large room out of layouts (with no walls)
    # check the rotation code, check that map can fill the room fully
    

    # todo next steps 30/10/2023:
    # (optional) 1. push my code
    # make the toggle between room_n and coverage ratio
    # investigate the connectivity issue:
        # start by breakpointing into master map generation, after each time it's updated, and then see if the map can be the issue