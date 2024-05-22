# "this .py file is the newest version"

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

# todo daria what does .resolve() do?
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

## rename THIS file from template_generator_new.py --> to mastermap_generator.py
## todo make into function, if i run here save onto disk, if i run elsewhere return mastermap.
## todo also make possible to generate multiple maps
## todo add parameter num_mmaps in config.yaml, aaaand the param where to save the maps generated
## for running it in the training loop, make it 1 map by default cause we don't need more.

## create a new file and a function inside of it and make the code inside the main as a new function 

## also, push code, clean code (by pusing), + make the new folder structure, + add the config file selection in the manual_control.py

# def generate_mastermap():

def normalize_dict_values(dictionary: dict):
    sum = 0
    value_sum = sum(dictionary.values())
    for key in dictionary:
        dictionary[key] = dictionary[key]/value_sum
        sum = sum + dictionary[key]


def user_intervention():
    user_choice = input("do you wish to exit? type y/n and press enter: ").strip()
    if user_choice == "y" or user_choice == "yes":
        print(f"you typed '{user_choice}'. program will now stop.")
        exit()
    elif user_choice == "n" or user_choice == "no":
        print(f"you typed '{user_choice}'. program will now continue running...")
    else:
        print("unintelligable input, program will now stop.")
        exit()

if __name__ == '__main__': # <-- make it into a function
    # TODO: Make into CLI tool
    # todo to find the bug, set random seeds and then pdb it

    config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "config_trial.yaml"
    args = MinyDict.from_yaml(config_path)
    breakpoint()
    maps = {} # maps is a dict with path: value, and it updates value on each entry of a map

    rnd_paths = {}

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

    for i in args.structure:
        # TODO turn each string path into Path
        # TODO make sure that directory paths ending with / and without are processed the same


        assert os.path.exists(i.path), f"path {i.path} doesn't exist. please replace it with a valid path."
        
        #if os.path.isdir(i.path) == True:
        #    print('todo, check that every element in the directory is a csv file')

        # todo, first we add all of the paths
        print(i)
        rnd_paths[i.path] = i.value
        """
        # then we randomly take one path
        # then if the randomly chosen path is a directory, we load only the csv files
        # if the randomly chosen path is a yaml file, we load the map on the fly

        file_list = []
        # if path is a directory, we add each .csv file that starts with "layout" in its name to file_list
        if os.path.isdir(i.path):
            if not i.path.endswith('/'):
                i.path = i.path + '/' # todo , temporary solution
            file_list = glob.glob(f"{i.path}layout*.csv")

        elif os.path.isfile(i.path):
            #breakpoint()
            file_path = i.path
#            if file_path.startswith('layout') and file_path.endswith('.csv')
            if file_path.endswith('.csv'):
                file_list = [file_path]

            print('hi daria')

        ##path_list.append(file_list)
        breakpoint()
        temp_maps = dict.fromkeys(file_list, i.value)
        # add new maps ("path: value" pairs), and for existing maps update values
        maps.update(temp_maps)
        print(maps)
        #breakpoint()

        print(len(glob.glob("/home/mila/d/daria.yasafova/mini_ada/Minigrid/minigrid/templates/layout*.csv")))
        print("ends with .csv", i.path.endswith('.csv'))
        print(i.path)
        print(i.value)
        """
    #breakpoint()

    
    breakpoint()
    normalize_dict_values(rnd_paths)


    breakpoint()
    drawn_path = choice(list(rnd_paths.keys()), 1, p=list(rnd_paths.values()))[0]

    # if it's a directory, we scoop all .csv files in it, assuming they are master maps
    breakpoint()
    if os.path.isdir(drawn_path):
        if not drawn_path.endswith('/'):
            drawn_path = drawn_path + '/' # todo , temporary solution
        file_list = glob.glob(f"{drawn_path}master_layout*.csv")

        # todo, return a list of maps

    elif os.path.isfile(drawn_path):
        #breakpoint()
        file_path = drawn_path
        if file_path.endswith('.csv'):
            file_list = [file_path]
            print(f"FYI: a single .csv file was chosen, the file is located at {file_path}.")
            print(f"FYI: if that is not the outcome you expected, change the paths among which the program will then randomly choose one. the paths can be changed in the config file at {config_path}.")
            user_intervention()

            # todo, return one map

        elif file_path.endswith(".yaml"):
            print(f"FYI: the program randomly chose a .yaml file, a map will be generated on the fly using the .yaml config at {file_path}.")
            print(f"FYI: if you expected a different outcome, change the settings in the config file at {config_path} by providing only path(s) to folders with .csv files of master maps")
            user_intervention()

            # todo daria 06.12.2023 generate a map
    breakpoint()

    


    mmap = MasterMap(height=args.map.height, width=args.map.width)

    timestamp = now()
    log_path = f'{LAYOUT_PATH}/log_{timestamp}.txt'
    
    args.pretty_print()

    ###breakpoint()

    if args.map.logic=="layout_count":
        # do sth

        number_of_items_to_pick = args.map.layout_count
        layouts = choice(list(maps.keys()), number_of_items_to_pick, p=list(maps.values()))
        smap_init = SubMap.from_csv(f"{layouts[0]}")
        mmap.init_submap_in_map(smap_init)
        # append_log(log_path, f'map : {layouts[0]}') # not needed, performed in the for loop below


        ####
        for i in range(len(layouts)):
            full_layout_path = f'{layouts[i]}'
            if i != 0:
                smap = SubMap.from_csv(f"{layouts[i]}")
                mmap.attempt_to_merge_maps(smap, rotation=True)
            cur_mmap = np.array(mmap.sync_map_using_obj_map())
            cur_map_coverage_ratio = 1 - cur_mmap[cur_mmap==None].size/cur_mmap.size
            append_log(log_path, f'map_{i}:{full_layout_path}')
            append_log(log_path, f'current_mmap_coverage_ratio (after adding the map above) : {cur_map_coverage_ratio}')
            #breakpoint()
            mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv") # store the intermediate master map


        
        ####

    elif args.map.logic == "coverage_ratio":
        # do sth else

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
        ###breakpoint()
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
            #breakpoint()
            mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv") # store the intermediate master map
            ##breakpoint()
            map_count = map_count + 1

        ###########

    mmap.update_map_tiles(state=GENERATION_STATE.END)

    # done, add timestamp to the name of the output file so that it doesn't overwrite
    mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{timestamp}.csv")

    # save configuration as log
    append_log(log_path, args)

    # questions, do we want repetitions?
    # how important is the "map filling" logic? can we drop it and instead go with the idea of increasing the master map for our needs? i.e. the user asks how many maps we want to merge and dance from there?
    #layouts = choice(list(maps.keys()), number_of_items_to_pick, p=list(maps.values())) # replaced this with the next, correction A
    
    ###breakpoint()

    #####
    # get a list of maps here by processing the map paths provided in the config.yaml file



    #####

    #mmap = MasterMap(height=config_dict['map']['height'], width=config_dict['map']['width']) # todo make height and width changable
    
    # todo what other parameters do we want?
    # todo randomly choose say 3 maps from LAYOUT_PATH
    # todo choose maps until the master map is full
    # todo given a set of maps, fill the master map with them until it's full
    # todo think of the condition of fullness
    # or todo fill the master map until 50/60/70 percent of the map is full

    # done changed logic
    
    # daria replaced this with layouts drawn by random weighted choice
    ##layouts_old = ['layouts_minigrid - layout_3_new_2.csv', 'layouts_minigrid - layout_4_new_5.csv', 'layouts_minigrid - layout_4_new_4.csv']
    ##smap_init = SubMap.from_csv(f"{LAYOUT_PATH}/{layouts[0]}")
    
    

    
    ## here to the for loop


    ###breakpoint()
    #mastermap = pd.DataFrame(np.array(mmap))
    


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
    # add pretty print for the config file params
    # todo fix first map repeating twice in the log file
    # todo, output the full name of the master map at the end

    # the idea is to test the current invironment
    # add exits
    # add another type of exits (exit(corridor), exit(room))
    # add rules associated with rooms only connecting to corridors and corridors to rooms
    # add corridors