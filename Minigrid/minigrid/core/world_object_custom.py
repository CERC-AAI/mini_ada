from __future__ import annotations

from typing import TYPE_CHECKING, Tuple
from minigrid.core.world_object import WorldObj

import numpy as np
import random
import math

from minigrid.core.constants import (
    COLOR_TO_IDX,
    COLORS,
    IDX_TO_COLOR,
    IDX_TO_OBJECT,
    OBJECT_TO_IDX,
    DIR_TO_VEC,
)

from minigrid.utils.rendering import (
    fill_coords,
    point_in_circle,
    point_in_line,
    point_in_rect,
    point_in_triangle,
    rotate_fn,
)

if TYPE_CHECKING:
    from minigrid.minigrid_env import MiniGridEnv
    from minigrid.envs.customv1 import CustomV1Env

Point = Tuple[int, int]


class WorldObjCustom(WorldObj):

    def test_and_resolve_overlap(self, env: CustomV1Env, obj: WorldObj) -> bool:
        """Can this overlap with the given object? 
        Assume that the tile is ready to accept the object if we get a true"""
        return obj is None
    
    def can_overlap(self) -> bool:
        """Can the agent overlap with this?"""
        return False
    
    def stepped_on(self, env: CustomV1Env, approach_position:Point) -> None:
        """Runs when agent is on the same tile as this object"""
        return
    
    def do_pickup(self, env: CustomV1Env) -> None:
        """Runs when agent picks up this object"""
        return False
    
    def do_dropped(self, env: CustomV1Env) -> None:
        """Runs when agent drops this object"""
        return False

    def can_pickup(self) -> bool:
        """Can the agent pick this up?"""
        return False

    def can_contain(self) -> bool:
        """Can this contain another object?"""
        return False

    def see_behind(self) -> bool:
        """Can the agent see behind this object?"""
        return True

    def toggle(self, env: MiniGridEnv, pos: tuple[int, int]) -> bool:
        """Method to trigger/toggle an action this object performs"""
        return False
    
    def step(self, env: CustomV1Env) -> None:
        """Runs each environment step"""
        return
    
    def hit_agent(self, env: CustomV1Env) -> None:
        """This object moved onto the agent during its step function"""
        return
    
    @property
    def step_order(self):
        """
        Ordering for objects to run their step function. 
        Agent is priority = 0
        Larger numbers come later in the queue
        Priority = np.nan means to not run step on this object
        """

        return 1


class Goal(WorldObjCustom):
    def __init__(self):
        super().__init__("floor", "green")

    def can_overlap(self):
        return True

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])

    def stepped_on(self, env: CustomV1Env, approach_position: Point) -> None:
        env.add_reward(env._reward())
        env.terminate()


class Floor(WorldObjCustom):
    """
    Colored floor tile the agent can walk over
    """

    def __init__(self, color: str = "blue"):
        super().__init__("floor", color)

    def can_overlap(self):
        return True

    def render(self, img):
        # Give the floor a pale color
        color = COLORS[self.color] / 2
        fill_coords(img, point_in_rect(0.031, 1, 0.031, 1), color)


class Lava(WorldObjCustom):
    def __init__(self):
        super().__init__("lava", "red")

    def can_overlap(self):
        return True

    def render(self, img):
        c = (255, 128, 0)

        # Background color
        fill_coords(img, point_in_rect(0, 1, 0, 1), c)

        # Little waves
        for i in range(3):
            ylo = 0.3 + 0.2 * i
            yhi = 0.4 + 0.2 * i
            fill_coords(img, point_in_line(0.1, ylo, 0.3, yhi, r=0.03), (0, 0, 0))
            fill_coords(img, point_in_line(0.3, yhi, 0.5, ylo, r=0.03), (0, 0, 0))
            fill_coords(img, point_in_line(0.5, ylo, 0.7, yhi, r=0.03), (0, 0, 0))
            fill_coords(img, point_in_line(0.7, yhi, 0.9, ylo, r=0.03), (0, 0, 0))

    def stepped_on(self, env: CustomV1Env, approach_position:Point) -> None:
        """Runs when agent is on the same tile as this object"""
        env.add_reward(-1)
        env.terminate()
        return


class Wall(WorldObjCustom):
    def __init__(self, color: str = "grey"):
        super().__init__("wall", color)

    def see_behind(self):
        return False

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])

    @property
    def step_order(self):
        return np.nan


class Door(WorldObjCustom):
    def __init__(self, color: str, is_open: bool = False, is_locked: bool = False):
        super().__init__("door", color)
        self.is_open = is_open
        self.is_locked = is_locked

    def can_overlap(self):
        """The agent can only walk over this cell when the door is open"""
        return self.is_open

    def see_behind(self):
        return self.is_open

    def toggle(self, env, pos):
        # If the player has the right key to open the door
        if self.is_locked:
            if isinstance(env.carrying, Key) and env.carrying.color == self.color:
                self.is_locked = False
                self.is_open = True
                return True
            return False

        self.is_open = not self.is_open
        return True

    def encode(self):
        """Encode the a description of this object as a 3-tuple of integers"""

        # State, 0: open, 1: closed, 2: locked
        if self.is_open:
            state = 0
        elif self.is_locked:
            state = 2
        # if door is closed and unlocked
        elif not self.is_open:
            state = 1
        else:
            raise ValueError(
                f"There is no possible state encoding for the state:\n -Door Open: {self.is_open}\n -Door Closed: {not self.is_open}\n -Door Locked: {self.is_locked}"
            )

        return (OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], state)

    def render(self, img):
        c = COLORS[self.color]

        if self.is_open:
            fill_coords(img, point_in_rect(0.88, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.92, 0.96, 0.04, 0.96), (0, 0, 0))
            return

        # Door frame and door
        if self.is_locked:
            fill_coords(img, point_in_rect(0.00, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.06, 0.94, 0.06, 0.94), 0.45 * np.array(c))

            # Draw key slot
            fill_coords(img, point_in_rect(0.52, 0.75, 0.50, 0.56), c)
        else:
            fill_coords(img, point_in_rect(0.00, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.04, 0.96, 0.04, 0.96), (0, 0, 0))
            fill_coords(img, point_in_rect(0.08, 0.92, 0.08, 0.92), c)
            fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), (0, 0, 0))

            # Draw door handle
            fill_coords(img, point_in_circle(cx=0.75, cy=0.50, r=0.08), c)


class Key(WorldObjCustom):
    def __init__(self, color: str = "blue"):
        super().__init__("key", color)

    def can_pickup(self):
        return True

    def render(self, img):
        c = COLORS[self.color]

        # Vertical quad
        fill_coords(img, point_in_rect(0.50, 0.63, 0.31, 0.88), c)

        # Teeth
        fill_coords(img, point_in_rect(0.38, 0.50, 0.59, 0.66), c)
        fill_coords(img, point_in_rect(0.38, 0.50, 0.81, 0.88), c)

        # Ring
        fill_coords(img, point_in_circle(cx=0.56, cy=0.28, r=0.190), c)
        fill_coords(img, point_in_circle(cx=0.56, cy=0.28, r=0.064), (0, 0, 0))


class Ball(WorldObjCustom):
    def __init__(self, color="blue"):
        super().__init__("ball", color)

    def can_pickup(self):
        return True

    def render(self, img):
        fill_coords(img, point_in_circle(0.5, 0.5, 0.31), COLORS[self.color])


class Box(WorldObjCustom):
    def __init__(self, color, contains: WorldObj | None = None):
        super().__init__("box", color)
        self.contains = contains

    def can_pickup(self):
        return True

    def render(self, img):
        c = COLORS[self.color]

        # Outline
        fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), c)
        fill_coords(img, point_in_rect(0.18, 0.82, 0.18, 0.82), (0, 0, 0))

        # Horizontal slit
        fill_coords(img, point_in_rect(0.16, 0.84, 0.47, 0.53), c)

    def toggle(self, env, pos):
        # Replace the box by its contents
        env.grid.set(pos[0], pos[1], self.contains)
        return True
    
class PushBox(WorldObjCustom):
    def __init__(self, color="grey"):
        super().__init__("box", color)

    def render(self, img):
        c = COLORS[self.color]

        # Outline
        fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), c)
        fill_coords(img, point_in_rect(0.18, 0.82, 0.18, 0.82), (0, 0, 0))

        # Horizontal slit
        fill_coords(img, point_in_rect(0.16, 0.84, 0.47, 0.53), c)

    def stepped_on(self, env: CustomV1Env, approach_position: Point) -> None:
        push_position = self.cur_pos + env.dir_vec
        push_obj = env.grid.get(*push_position)

        if self.test_and_resolve_overlap(env, push_obj):
            env.remove_obj(*self.cur_pos)

            env.agent_pos = self.cur_pos

            env.put_obj(self, *push_position)

        return super().stepped_on(env, approach_position)

class AIAgent(WorldObjCustom):
    def __init__(self, color="blue"):
        super().__init__("box", color)
        self.direction = random.randint(0, 3)  # 0: Right, 1: Down, 2: Left, 3: Up

    def render(self, img):
        fill_coords(img, point_in_circle(0.5, 0.5, 0.31), COLORS[self.color])

    @property
    def dir_vec(self):
        """
        Get the direction vector for the agent, pointing in the direction
        of forward movement.
        """

        assert (
            self.direction >= 0 and self.direction < 4
        ), f"Invalid direction: {self.direction} is not within range(0, 4)"
        return DIR_TO_VEC[self.direction]

    def step(self, env: CustomV1Env) -> None:
        # Get the position in front of the agent
        fwd_pos = self.cur_pos + self.dir_vec

        # Get the contents of the cell in front of the agent
        fwd_cell = env.grid.get(*fwd_pos)

        if fwd_cell is None or fwd_cell.test_and_resolve_overlap(env, fwd_cell):
            env.remove_obj(*self.cur_pos)
            env.put_obj(self, *fwd_pos)
        else: 
            # Turn left
            self.direction = (self.direction + 1) % 4

    def render(self, img):
        c = COLORS[self.color]

        if self.direction is not None:
            tri_fn = point_in_triangle(
                (0.12, 0.19),
                (0.87, 0.50),
                (0.12, 0.81),
            )

            print(self.direction)

            # Rotate the agent based on its direction
            tri_fn = rotate_fn(tri_fn, cx=0.5, cy=0.5, theta=0.5 * math.pi * self.direction)
            fill_coords(img, tri_fn, c)

    def encode(self) -> tuple[int, int, int]:
        """Hack the custom value while we think of a new indexing method"""
        return (OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], 100 + self.direction)
    

    def hit_agent(self, env: CustomV1Env) -> None:
        env.add_reward(-1)
        env.terminate()
        return
    