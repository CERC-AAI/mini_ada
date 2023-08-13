from __future__ import annotations

from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Door, Goal, Key, Ball, Box, Lava, Wall
from minigrid.minigrid_env import MiniGridEnv
from pathlib import Path
import pandas as pd

LAYOUT_PATH = Path(__file__).resolve().parent.parent / 'templates/master_layout.csv'

OBJ_DICT = {
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

    return obj_dict

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

    def __init__(self, max_steps: int | None = None, **kwargs):
        print(kwargs)
        if "size" in kwargs:
            kwargs.pop("size")
        map_arr = pd.read_csv(LAYOUT_PATH, header=None).to_numpy()
        size = len(map_arr)
        self.map_info = get_obj_coords(map_arr, OBJ_DICT)
        print(self.map_info)
        # height, width = self.map_info['Height']+2, self.map_info['Width']+2
        height, width = self.map_info['Height'], self.map_info['Width']

        if max_steps is None:
            max_steps = 10 * size**2
        mission_space = MissionSpace(mission_func=self._gen_mission)
        super().__init__(
            mission_space=mission_space, height=height, width=width, max_steps=max_steps, **kwargs
        )
        # super().__init__(
        #     mission_space=mission_space, grid_size=size, max_steps=max_steps, **kwargs
        # )

    @staticmethod
    def _gen_mission():
        return "use the key to open the door and then get to the goal"

    def _gen_grid(self, width, height):
        # Note: Minigrid uses (col, row) indexing, with top being (0,0) by default
        # Create an empty grid
        self.grid = Grid(width, height)

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
        self.agent_pos = (self.map_info['Agent'][0][0], self.map_info['Agent'][0][1])
        # Agent init direction: Can be random or deterministic
        self.agent_dir = self._rand_int(0, 4)

        # Place a door in the wall
        # doorIdx = self._rand_int(1, width - 2)
        for obj_type in self.map_info:
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
                    self.put_obj(Wall(), obj[0], obj[1])
                  

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

        self.mission = "use the key to open the door and then get to the goal"
