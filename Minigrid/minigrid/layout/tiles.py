import numpy as np
import pandas as pd
import re
import random
import importlib
from typing import TYPE_CHECKING, Tuple

from minigrid.layout.constants import GENERATION_STATE


Point = Tuple[int, int]


def get_class_from_tile_str(tile_str):
    if tile_str is None:
        return None, None
    
    name, params = split_function_definition(tile_str)

    module = importlib.import_module("minigrid.layout.tiles")

    object_class = getattr(module, name.strip())
    
    return object_class, params

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

class Tile:
    def __init__(self, tile_type:str, position: Point=(0,0), params=[]):
        self.tile_type = tile_type
        self.position = position
        self.params = params
        
    def get_tile_str_repr(self) -> str:
        if len(self.params) > 0:
            return f'{self.tile_type}({";".join(self.params)})'
        else:
            return f'{self.tile_type}'
    
    def can_overlap_tile(self, incoming_tile) -> bool:
        return False
    
    def resolve_overlap(self, incoming_tile):
        return self
    
    def update(self, state: GENERATION_STATE):
        return self

class Agent(Tile):
    def __init__(self, position: Point=(0,0), params=[]):
        super().__init__(tile_type="Agent", position=position, params=params)

class Wall(Tile):
    def __init__(self, position: Point=(0,0), params=[]):
        super().__init__(tile_type="Wall", position=position, params=params)
    
    def can_overlap(self):
        return False
    
    def resolve_overlap(self, incoming_tile):
        return self
    
    def update(self, state):
        return self

class Space(Tile):
    def __init__(self, position: Point=(0,0), params=[]):
        super().__init__(tile_type="Space", position=position, params=params)
    
    def can_overlap_tile(self, incoming_tile: Tile) -> bool:
        return True
    
    def resolve_overlap(self, incoming_tile: Tile) -> Tile:
        return incoming_tile


class Exit(Tile):
    def __init__(self, position: Point=(0,0), params=[]):
        super().__init__(tile_type="Exit", position=position, params=params)
    
    def can_overlap_tile(self, incoming_tile: Tile) -> bool:
        return True
    
    def resolve_overlap(self, incoming_tile: Tile) -> Tile:
        return incoming_tile
    
    def update(self, state: GENERATION_STATE) -> Tile:
        if state == GENERATION_STATE.MERGE:
            return Space(position=self.position)
        
        elif state == GENERATION_STATE.END:
            return Wall(position=self.position)

class Undf(Tile):
    def __init__(self, position: Point=(0,0), params=[]):        
        super().__init__(tile_type="Undf", position=position, params=params)
    
    
    def get_tile_str_repr(self) -> str:
        return f"Undf({self.params[0]})"
    
    def can_overlap_tile(self, incoming_tile: Tile) -> bool:
        return True
    
    def resolve_overlap(self, incoming_tile: Tile) -> Tile:
        return incoming_tile
    
    def update(self, state: GENERATION_STATE) -> Tile:
        if state == GENERATION_STATE.MERGE:
            return self
        
        elif state == GENERATION_STATE.END:
            new_tile, _ = get_class_from_tile_str(self.params[0])
            new_tile = new_tile(position=self.position, params=self.params[1:])
            return new_tile