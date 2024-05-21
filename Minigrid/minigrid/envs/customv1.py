from __future__ import annotations

from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object_custom import *
from minigrid.minigrid_env import MiniGridEnv
from pathlib import Path
import pandas as pd
import hashlib
import math
from abc import abstractmethod
from typing import Any, Iterable, SupportsFloat, TypeVar
import importlib
import re
import inspect
import os

import gymnasium as gym
import numpy as np
import pygame
import pygame.freetype
from gymnasium import spaces
from gymnasium.core import ActType, ObsType

from minigrid.core.actions import Actions
from minigrid.core.constants import COLOR_NAMES, DIR_TO_VEC, TILE_PIXELS
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
#from minigrid.templates.mastermap_generator import generate_mastermap # todo
from minigrid.templates.mastermap_generator import generate_mastermap

from minydra import MinyDict

LAYOUT_PATH = Path(__file__).resolve().parent.parent / 'templates/master_layout.csv'

'''OBJ_DICT = {
    'Key': set(),
    'Door': set(),
    'Goal': set(),
    'Agent': set(),
    'Wall': set(),
    'Ball': set(),
    'Box': set(),
    'Lava': set(),
    'Width': None,
    'Height': None,
}

def get_obj_coords(map_arr, input_obj_dict):
    obj_dict = input_obj_dict.copy()

    height = len(map_arr)
    width = len(map_arr[0])
    obj_dict['Width'] = width
    obj_dict['Height'] = height
    
    for row in range(height):
        for col in range(width):
            cell_type = map_arr[row][col]
            if cell_type in obj_dict:
                # Gym is (col, row) format
                obj_dict[cell_type].add((col, row))

    # Convert the object info set back into iterable list
    for obj, info in obj_dict.items():
        if type(info) == set:
            obj_dict[obj] = list(info)
        else:
            obj_dict[obj] = info

    return obj_dict'''

def strings_to_function_params(string_array, function):
    parameters = inspect.signature(function).parameters

    for k, param in enumerate(parameters):
        if k < len(string_array):
            variable_type = parameters[param].annotation

            if variable_type.lower() == 'bool':
                string_array[k] = not string_array[k].lower() == 'false'
            else:
                string_array[k] = __builtins__[variable_type](string_array[k])
        else:
            break

    return string_array


def split_function_definition(definition_string):
    # Define a regular expression pattern to match the function name and parameters
    pattern = r'(\w+)\((.*?)\)'

    # Use re.match to find the match at the beginning of the string
    match = re.match(pattern, definition_string)

    if match:
        # Extract the function name (group 1) and parameters (group 2)
        function_name = match.group(1)
        parameters = match.group(2).split(';')
        return function_name, parameters
    else:
        pattern = r'(\w+)'
        match = re.match(pattern, definition_string)
        
        if match:
            function_name = match.group(1)
            parameters = []
            return function_name, parameters
        else:
            raise ValueError("Invalid function definition format")

# todo get familiar with the class
class CustomV1Env(MiniGridEnv):
 
    """
    ## Description

    This environment has a key that the agent must pick up in order to unlock a
    goal and then get to the green goal square. This environment is difficult,
    because of the sparse reward, to solve using classical RL algorithms. It is
    useful to experiment with curiosity or curriculum learning.

    ## Mission Space

    "use the key to open the door and then get to the goal"

    ## Action Space

    | Num | Name         | Action                    |
    |-----|--------------|---------------------------|
    | 0   | left         | Turn left                 |
    | 1   | right        | Turn right                |
    | 2   | forward      | Move forward              |
    | 3   | pickup       | Pick up an object         |
    | 4   | drop         | Unused                    |
    | 5   | toggle       | Toggle/activate an object |
    | 6   | done         | Unused                    |

    ## Observation Encoding

    - Each tile is encoded as a 3 dimensional tuple:
        `(OBJECT_IDX, COLOR_IDX, STATE)`
    - `OBJECT_TO_IDX` and `COLOR_TO_IDX` mapping can be found in
        [minigrid/minigrid.py](minigrid/minigrid.py)
    - `STATE` refers to the door state with 0=open, 1=closed and 2=locked

    ## Rewards

    A reward of '1 - 0.9 * (step_count / max_steps)' is given for success, and '0' for failure.

    ## Termination

    The episode ends if any one of the following conditions is met:

    1. The agent reaches the goal.
    2. Timeout (see `max_steps`).

    ## Registered Configurations

    - `MiniGrid-DoorKey-5x5-v0`
    - `MiniGrid-DoorKey-6x6-v0`
    - `MiniGrid-DoorKey-8x8-v0`
    - `MiniGrid-DoorKey-16x16-v0`

    """

    def __init__(self, config_path, max_steps: int | None = None, **kwargs):
        print(kwargs)
        layout = LAYOUT_PATH
        if "layout" in kwargs:
            layout = kwargs.pop("layout")
            layout = Path(__file__).resolve().parent.parent / f'templates/{layout}.csv'
        
        self.map_arr = pd.read_csv(layout, header=None).to_numpy()
        self.default_map_arr = self.map_arr
        #breakpoint()
        self.config_path = config_path # todo daria check
        self.args = MinyDict.from_yaml(config_path)

        
        if self.args.root_folder == "__minigrid_folder__":
            self.args.root_folder = f"{Path(__file__).parent.parent.resolve()}"
        elif self.args.root_folder == "__miniada_folder__":
            self.args.root_folder = f"{Path(__file__).parent.parent.parent.parent.resolve()}"
        #self.seed(42) # todo this doesn't work
        #self.map_info = get_obj_coords(map_arr, OBJ_DICT)
        #print(self.map_info)
        # height, width = self.map_info['Height']+2, self.map_info['Width']+2
        #height, width = self.map_info['Height'], self.map_info['Width']
        
        height = self.args.map.height
        width = self.args.map.width
        #height = self.args.map.width
        #width = self.args.map.height
        
        if max_steps is None:
            max_steps = 10 * height * width
        mission_space = MissionSpace(mission_func=self._gen_mission)
        super().__init__(
            mission_space=mission_space, height=height, width=width, max_steps=max_steps, **kwargs
        )

        self.obj_list = []
        # super().__init__(
        #     mission_space=mission_space, grid_size=size, max_steps=max_steps, **kwargs
        # )

    # todo task load a random map or a generate a new map
    # either get a large corpus of maps or generate maps on the fly (possibly with a new seed each time)

    """
    resets an episode, gets recalled each new episode
    """
    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        self.obj_list = []

        self.seed_n = np.random.randint(1000000) # todo save then in logs or wandb
        #self.seed(self.seed_n)

        # todo daria set a bunch of parameters, where i'm loading from (for 1. get a large corpus of maps)

        # todo write a code for generating masterms on the fly as well as pulling ready to use mastermaps using the config
        #breakpoint()
        #for i in range():
        #    mmap = generate_mastermap()
       #     #mmap.to_csv(f"{LAYOUT_PATH}/master_layout_{i}.csv")
        #breakpoint()
        mmap = generate_mastermap(self.args)
        self.map_arr = np.array(mmap.sync_map_using_obj_map())
        self.default_map_arr = self.map_arr
        #breakpoint()
        os.makedirs(f"{self.args.root_folder}/{self.args.map.output_folder}", exist_ok=True)
        mmap.to_csv(f"{self.args.root_folder}/{self.args.map.output_folder}/master_layout_101.csv")
        #mmap.to_csv(f"{LAYOUT_PATH}/master_layout_101.csv")
        
        #height = len(self.map_arr)
        #width = len(self.map_arr[0])
        #breakpoint()

        return super().reset(seed=seed, options=options)

    @staticmethod
    def _gen_mission():
        return "use the key to open the door and then get to the goal"

    def _gen_grid(self, width, height):
        # Note: Minigrid uses (col, row) indexing, with top being (0,0) by default
        # Create an empty grid
        #self.grid = Grid(width, height)
        self.grid = Grid(height, width)

        module = importlib.import_module("minigrid.core.world_object_custom")

        agent_placed = False
        for i in range(self.width):
            for j in range(self.height):
        #for i in range(self.height):
        #    for j in range(self.width):
                #breakpoint()
                #object_string = self.map_arr[j, i] # daria we swapped the coordinates
                object_string = self.map_arr[i, j]

                object_name, params = split_function_definition(object_string)

                if object_name == "Agent":
                    self.agent_pos = (j, i)
                    #self.agent_pos = (i, j)

                    agent_placed = True

                    if len(params) > 0:
                        self.agent_dir = params[0]
                    else:
                        self.agent_dir = self._rand_int(0, 4)
                elif hasattr(module, object_name):
                    object_class = getattr(module, object_name)
                    params = strings_to_function_params(params, object_class)
                    object = object_class(*params)

                    self.put_obj(object, j, i)
                    #self.put_obj(object, i, j)

                #self.put_obj(Door("yellow", is_locked=True), obj[0], obj[1])

        self.place_obj(AIAgent())

        if not agent_placed:
            self.place_agent()
        # Generate the surrounding walls
        # self.grid.wall_rect(0, 0, width, height)

        # Place a goal in the bottom-right corner
        # Coord (width-1, height-1) is a wall
        # self.put_obj(Goal(), width - 2, height - 2)
        # Init only the first goal in the list: only 1 goal allowed
        # self.put_obj(Goal(), self.map_info['Goal'][0][0], self.map_info['Goal'][0][1])

        # Create a vertical splitting wall
        # TODO: Integrate wall into the loop with other objects, figure out various configurations of wall
        # for wall in self.map_info['Wall']:
        #     self.grid.vert_wall(wall[0], 0)

        # Place the agent at a random position and orientation
        # on the left side of the splitting wall
        # self.place_agent(size=(splitIdx, height))
        # Init only the first agent in the list: only 1 agent allowed
        # self.agent_pos = (self.map_info['Agent'][0][0], self.map_info['Agent'][0][1])
        # Agent init direction: Can be random or deterministic
        # self.agent_dir = self._rand_int(0, 4)

        # Place a door in the wall
        # doorIdx = self._rand_int(1, width - 2)
        '''for obj_type in self.map_info:
            if obj_type == 'Door':
                # TODO: Keys with different colors
                for obj in self.map_info[obj_type]:
                    self.put_obj(Door("yellow", is_locked=True), obj[0], obj[1])
            elif obj_type == 'Key':
                # TODO: Keys with different colors
                for obj in self.map_info[obj_type]:
                    self.put_obj(Key("yellow"), obj[0], obj[1])
            elif obj_type == 'Lava':
                for obj in self.map_info[obj_type]:
                    self.put_obj(Lava(), obj[0], obj[1])
            elif obj_type == 'Box': 
                # TODO: Boxes with different colors
                for obj in self.map_info[obj_type]:
                    self.put_obj(Box("blue"), obj[0], obj[1])
            elif obj_type == 'Ball':
                # TODO: Balls with different colors
                for obj in self.map_info[obj_type]:
                    self.put_obj(Ball("red"), obj[0], obj[1])
            elif obj_type == 'Wall':
                # TODO: Balls with different colors
                for obj in self.map_info[obj_type]:
                    self.put_obj(Wall(), obj[0], obj[1])'''
                  

        # Place a yellow key on the left side
        # self.place_obj(obj=Key("yellow"), top=(0, 0), size=(splitIdx, height))
        # for obj in self.map_info['Key']:
        #     self.put_obj(Key("yellow"), key[0], key[1])

        # for key in self.map_info['Lava']:
        #             self.put_obj(Lava(), key[0], key[1])

        # for key in self.map_info['Box']:
        #                     self.put_obj(Box("blue"), key[0], key[1])

        # for key in self.map_info['Ball']:
        #                     self.put_obj(Ball("red"), key[0], key[1])

        self.place_obj(Goal())

        self.mission = "use the key to open the door and then get to the goal"

    def step(
        self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        self.step_count += 1

        self.reward = 0
        self.terminated = False
        truncated = False

        # Get the position in front of the agent
        fwd_pos = self.front_pos

        # Get the contents of the cell in front of the agent
        fwd_cell = self.grid.get(*fwd_pos)

        # Do object step functions
        sorted_objects = sorted(self.obj_list, key=lambda x: x.step_order)

        for object in sorted_objects:
            if object.step_order < 0:
                object.step()
            else:
                break

        #Do agent step functions

        # Rotate left
        if action == self.actions.left:
            self.agent_dir -= 1
            if self.agent_dir < 0:
                self.agent_dir += 4

        # Rotate right
        elif action == self.actions.right:
            self.agent_dir = (self.agent_dir + 1) % 4

        # Move forward
        elif action == self.actions.forward:
            approach_position = self.agent_pos

            if fwd_cell is None or fwd_cell.can_overlap():
                self.agent_pos = tuple(fwd_pos)     
            if fwd_cell is not None:
                fwd_cell.stepped_on(self, approach_position)

        # Pick up an object
        elif action == self.actions.pickup:
            if fwd_cell and fwd_cell.can_pickup():
                if self.carrying is None:
                    self.carrying = fwd_cell
                    self.carrying.cur_pos = np.array([-1, -1])
                    self.grid.set(fwd_pos[0], fwd_pos[1], None)

                    fwd_cell.do_pickup(self)

        # Drop an object
        elif action == self.actions.drop:
            if not fwd_cell and self.carrying:
                self.grid.set(fwd_pos[0], fwd_pos[1], self.carrying)
                self.carrying.cur_pos = fwd_pos
                self.carrying = None

                fwd_cell.do_dropped(self)

        # Toggle/activate an object
        elif action == self.actions.toggle:
            if fwd_cell:
                fwd_cell.toggle(self, fwd_pos)

        # Done action (not used by default)
        elif action == self.actions.done:
            pass

        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Finish object steps
        
        for object in sorted_objects:
            if object.step_order >= 0:
                object.step(self)

        current_cell = self.grid.get(*self.agent_pos)

        if not current_cell is None:
            current_cell.hit_agent(self)

        if self.step_count >= self.max_steps:
            truncated = True

        if self.render_mode == "human":
            self.render()

        obs = self.gen_obs()

        return obs, self.reward, self.terminated, truncated, {}
    
    # todo daria add a similar function terminate_trial, that resets the environment (does all the stuff that resets stuff without randomization / returns the environment to it's original state)
    def terminate(self):
        self.terminated = True

    def terminate_trial(self):
        # call self.map_arr here after calling reset to change if changing self.map_arr in reset changes it everywhere
        self.terminated = True

    """
    restarts a trial
    """
    def restart():
        # todo daria set seed
        #self.seed(self.seed_n)
        return None

    def add_reward(self, reward:float):
        self.reward += reward
    
    def place_obj(
        self,
        obj: WorldObj | None,
        top: Point = None,
        size: tuple[int, int] = None,
        reject_fn=None,
        max_tries=math.inf,
    ):
        if obj is not None and reject_fn is not None:
            reject_fn = lambda env, pos : not obj.test_and_resolve_overlap(env, env.grid.get(*pos)) and reject_fn(env, pos)
        elif obj is not None:
            reject_fn = lambda env, pos : not obj.test_and_resolve_overlap(env, env.grid.get(*pos))

        place_position = (-1, -1)
        try:
            place_position = super().place_obj(obj=obj, top=top, size=size, reject_fn=reject_fn, max_tries=max_tries)

            if (not obj is None and not obj.step_order is np.nan and not obj in self.obj_list):
                self.obj_list.append(obj)
        except:
            pass

        return place_position
    
    def put_obj(self, obj: WorldObj, i: int, j: int):
        """
        Put an object at a specific position in the grid
        """

        self.grid.set(i, j, obj)
        obj.init_pos = (i, j)
        obj.cur_pos = (i, j)
        #self.grid.set(j, i, obj)
        #obj.init_pos = (j, i)
        #obj.cur_pos = (j, i)

        if (not obj.step_order is np.nan and not obj in self.obj_list):
            self.obj_list.append(obj)

    def remove_obj(self, i: int, j: int):
        """
        Put an object at a specific position in the grid
        """

        old_obj = self.grid.get(i, j)
        self.grid.set(i, j, None)
        #old_obj = self.grid.get(j, i)
        #self.grid.set(j, i, None)

        if (old_obj in self.obj_list):
            self.obj_list.remove(old_obj)