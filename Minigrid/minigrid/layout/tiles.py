from .constants import STATE_END_MERGES, STATE_MERGE

class Tile:
    def __init__(self, tile_type, position):
        self.tile_type = tile_type
        self.position = position
        
    def get_tile_str_repr(self):
        return self.tile_type
    
    def can_overlap(self):
        pass
    
    def resolve_overlap(self, tile):
        pass
    
    def update(self, state):
        pass
    
class Wall(Tile):
    def __init__(self, position):
        super().__init__(tile_type="Wall", position=position)
    
    def can_overlap(self):
        return False
    
    def resolve_overlap(self, incoming_tile):
        return self
    
    def update(self, state):
        return self

class Space(Tile):
    def __init__(self, position):
        super().__init__(tile_type="Space", position=position)
    
    def can_overlap(self):
        return True
    
    def resolve_overlap(self, incoming_tile):
        return incoming_tile
    
    def update(self, state):
        return self


class Exit(Tile):
    def __init__(self, position):
        super().__init__(tile_type="Exit", position=position)
    
    def can_overlap(self):
        return True
    
    def resolve_overlap(self, incoming_tile):
        return incoming_tile
    
    def update(self, state):
        if state == STATE_MERGE:
            return Space(position=self.position)
        
        elif state == STATE_END_MERGES:
            return Wall(position=self.position)

class Undefined(Tile):
    def __init__(self, position, payload=None):
        self.payload = payload
        
        self.alt_mapping = {
            'Wall': Wall(position),
            'Space': Space(position),
        }
        
        super().__init__(tile_type="Undf", position=position)
    
    def get_tile_str_repr(self):
        return f"Undf({self.payload})"
    
    def can_overlap(self):
        return True
    
    def resolve_overlap(self, incoming_tile):
        return incoming_tile
    
    def update(self, state):
        if state == STATE_MERGE:
            return self
        
        elif state == STATE_END_MERGES:
            return self.alt_mapping[self.payload]