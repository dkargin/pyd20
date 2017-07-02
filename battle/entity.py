import math
from .grid import Point

# Grid entity
class Entity:
    def __init__(self, **kwargs):
        # Current tile coordinates
        self.x = 0
        self.y = 0
        # Current visual coordinates. Most of time it is equal to tile coordinates
        self.visual_X = 0.0
        self.visual_Y = 0.0
        # Body size, in tiles
        self._size = kwargs.get('size', 1)
        self._occupation_template = None
        # Should we keep a list of threatened tiles when we have occupation template?
        self._threatened_tiles = []
        self._occupied_tiles = []

    def get_size(self):
        return self._size

    def get_center(self) -> Point:
        return Point(x=(self.x + self._size*0.5), y=self.y + self._size*0.5)

    def get_coord(self) -> Point:
        return Point(x=self.x, y=self.y)

    def distance_melee(self, other):
        center_self = self.get_center()
        center_other = other.get_center()
        return center_self.distance_melee(center_other) - other.get_size() * 0.5

    def get_occupation_template(self):
        return self._occupation_template

    def set_occupation_template(self, template):
        self._occupation_template = template

    # Return distance between tiles
    @staticmethod
    def distance_tiles(obj_a, obj_b):
        return math.sqrt((obj_a.x - obj_b.y) ** 2 + (obj_a.y - obj_b.y) ** 2)

    # Check if combatant obj_b is whithin reach of combatant obj_a
    def is_adjacent(self, other):
        reach = self.total_reach()
        distance = self.distance_melee(other)
        return reach > distance

    def fix_visual(self):
        self.visual_X = self.x
        self.visual_Y = self.y



