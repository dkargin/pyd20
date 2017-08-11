import random
import math
from .core import unit_length

TERRAIN_OUTSIDE = -1
TERRAIN_FREE = 0
TERRAIN_GRASS = 1
TERRAIN_WALL = 10


class Point:
    """
    Generic 2d point/vector
    """
    def __init__(self, **kwargs):
        self.x = kwargs.get('x', 0.0)
        self.y = kwargs.get('y', 0.0)

    def tuple(self):
        return self.x, self.y

    def __add__(self, other):
        return Point(x=self.x+other.x, y=self.y+other.y)

    def __sub__(self, other):
        return Point(x=self.x-other.x, y=self.y-other.y)

    def __mul__(self, scale):
        return Point(x=self.x*scale, y=self.y * scale)

    def len(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    def normalize(self):
        """
        Calculates normalized vector
        :return: Point - normalized vector
        """
        l = self.len()
        if l == 0:
            l = 1
        return Point(x=self.x/l, y=self.y/l)

    # Manhattan metric
    def distance_melee(self, b):
        return max(abs(self.x - b.x), abs(self.y - b.y))

    # Euclidian metric
    def distance_tiles(self, b):
        return math.sqrt((self.x - b.x)**2 + (self.y - b.y)**2)

    def distance(self, b):
        return self.distance_tiles(b)*5

    def distance_xy(self, x, y):
        return math.sqrt((self.x - x)**2 + (self.y - y)**2) * 5

    def __str__(self):
        return "(%d;%d)" % (self.x, self.y)

    def __repr__(self):
        return "Point(%d;%d)" % (self.x, self.y)


def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]

    Obtained from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


class Grid(object):

    """
    Implements a battle grid. [The grid] consists of a grid of 1-inch squares.
    Each of these squares represents a 5-foot square in the game world (D&D 3.5 Players Handbook, p.133).

    :type _size: int
    :type __grid: Tile[]
    """

    def __init__(self, width, height):
        """
        Creates a Grid object
        """
        self._size = 5.0
        self.set_tile_size(5.0)
        self._width = width
        self._height = height
        self._revision = 0
        self.__grid = []

        # Maps tuple (size, reach, near, far) -> OccupancyTemplate
        self._occupancy_templates = {}

        for y in range(0, height):
            for x in range(0, width):
                self.__grid.append(Tile(x, y))

    def set_tile_size(self, size):
        """
        sets the tile size in the current unit

        :param float size: the new tile size
        """
        self._size = size / unit_length

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_tilesize(self):
        """
        returns size of a tile in the current unit

        :rtype: int
        """
        return self._size * unit_length

    def is_inside(self, x, y):
        return x in range(0, self._width) and y in range(0, self._height)

    # Get random free tile
    def get_free_tile(self):
        free = []
        for tile in self.__grid:
            if tile.is_empty():
                free.append(tile)
        if len(free) > 0:
            index = random.randint(0, len(free)-1)
            tile = free[index]
            return tile.x, tile.y
        else:
            return None

    def get_tile_range(self, center, distance):
        """
        :param center: - center tile
        :param distance: - tile range
        :return: [] array of selected tiles
        """
        tiles = []
        for y in range(math.floor(center.y - distance), math.ceil(center.y + distance)):
            for x in range(math.floor(center.x - distance), math.ceil(center.x + distance)):
                tile = self.get_tile(x,y)
                if tile is not None:
                    tiles.append(tile)
        return tiles

    # Projecting some entity to a map
    # Each cell, occupied by an entity, will keep reference to an entity
    # All threatened tiles will keep references as well
    def register_entity(self, entity):
        # Obtain occupation template
        template = entity.get_occupation_template()
        if not isinstance(template, OccupationTemplate):
            # Generate new occupation template
            template = self.get_occupancy_template(entity)
            entity.set_occupation_template(template)

        def offset_tile(coord) -> Tile:
            return self.get_tile(coord[0] + entity.x, coord[1] + entity.y)

        # Occupying tiles
        for offset in template.tiles_occupied:
            tile = offset_tile(offset)
            if tile is not None and entity not in tile.occupation:
                tile.occupation.append(entity)
                if tile not in entity.occupied_tiles:
                    entity.occupied_tiles.append(tile)

        # Mark threatened area
        for offset in template.tiles_threatened:
            tile = offset_tile(offset)
            if tile is not None and entity not in tile.threaten:
                tile.threaten.append(entity)
                if tile not in entity.threatened_tiles:
                    entity.threatened_tiles.append(tile)

        self._revision += 1

    # Remove entity from grid.
    # Removes all the references, and tile threatening as well
    def unregister_entity(self, entity):
        for tile in entity._threatened_tiles:
            tile.threaten.remove(entity)
        entity._threatened_tiles = []

        for tile in entity._occupied_tiles:
            tile.occupation.remove(entity)
        entity._occupied_tiles = []

        self._revision += 1

    @property
    def revision(self):
        return self._revision

    def set_terrain(self, x, y, t):
        """
        Set terrain type for a tile
        :param x:int x coordinate of a tile
        :param y:int y coordinate of a tile
        :param t:int terrain type
        """
        tile = self.get_tile(x, y)

        if tile.set_terrain(t):
            self._revision += 1

    # Get tile reference
    def get_tile(self, x, y):
        """
        returns the tile at position x/y

        :param int x: the x coordinate of the tile
        :param int y: the y coordinate of the tile
        :rtype: Tile
        """
        if self.is_inside(x, y):
            return self.__grid[x + y * self._width]
        return None

    # Get tile area
    def get_adjacent_tiles(self, tile):
        """
        returns tiles that are adjacent to the tile

        :param Tile tile: the tile
        :rtype: Tile[]
        """
        x = tile.x
        y = tile.y
        xs = [x-1, x, x+1]
        ys = [y-1, y, y+1]
        adjacent_tiles = []
        for tx in xs:
            for ty in ys:
                if tx == x and ty == y:
                    continue
                tile = self.get_tile(tx, ty)
                if tile is not None:
                    adjacent_tiles.append(tile)
        return adjacent_tiles

    # Get occupancy template for specified parameters
    # This templates are cached
    def get_occupancy_template(self, entity):
        size = entity.get_size()
        base_reach = entity.natural_reach()
        near = entity.has_reach_near()
        far = entity.has_reach_far()

        key = (size, base_reach, near, far)

        if key in self._occupancy_templates:
            return self._occupancy_templates[key]

        new_template = OccupationTemplate(size, base_reach, far, near)
        self._occupancy_templates[key] = new_template
        return new_template

    def get_tiles(self):
        """
        Returns all tiles

        :rtype: Tile[]
        """
        return self.__grid

    def __repr__(self):
        max_x = 0
        max_y = 0
        for tile in self.__grid:
            if tile.x > max_x:
                max_x = tile.x
            if tile.y > max_y:
                max_y = tile.y

        result = "<Grid>\n"
        for y in range(1, max_y):
            for x in range(1, max_x):
                result += " | " + str(self.get_tile(x, y))
            result += " |\n"
        result += "</Grid>"
        return result


class Tile(object):
    """
    Implements a tile on a Grid.

    :type x: int
    :type y: int
    :type terrain: int
    :type occupation: list
    :type threaten: list
    """
    def __init__(self, x, y):
        """
        Creates a Tile object
        :param int x: The x position of the Tile
        :param int y: The y position of the Tile
        """
        self.x = x
        self.y = y
        # Max size allowed to be in this tile
        self._max_size = 10

        self.occupation = []
        self.terrain = TERRAIN_FREE
        # Objects that threaten this tile
        self.threaten = []

    def is_empty(self):
        """
        returns whether the Tile is occupied or not

        :rtype: bool
        """
        return len(self.occupation) == 0 and self.terrain != TERRAIN_WALL

    def get_coord(self):
        return Point(x=self.x, y=self.y)

    def set_terrain(self, t):
        self.terrain = t

    def has_occupation(self, thing):
        """
        returns whether the thing occupies this tile or not

        :param thing: the thing to check
        :rtype: bool
        """
        return thing in self.occupation

    def is_threatened(self, combatant):
        if len(self.threaten) == 0:
            return False
        return True

    def __repr__(self):
        return "<Tile " + str(self.x) + "x" + str(self.y) + " " + str(self.occupation) + ">"

    def __hash__(self):
        return id(self)


# Reach templates for different creature sizes and reaches
# NOTE: reach weapon are doubling natural reach
class OccupationTemplate:
    MARK_OCCUPY = 1
    MARK_THREATEN_NEAR = 2
    MARK_THREATEN_FAR = 4

    def __init__(self, size, reach, far=False, near=True):
        self.size = size
        self.reach = reach
        self.far = far
        self.near = near
        # List of triplets {x, y, role}, where x and y - relative coordinates, role = tile role
        self.template = []
        self.tiles_occupied = []
        self.tiles_threatened = []
        self.tiles_adjacent = []
        self.block_size = 0
        self.offset = 0
        self.build()

    def build(self):
        reach = self.reach
        far_reach = self.reach
        size = self.size

        if self.far:
            far_reach *= 2

        # Returns if cell is occupied by this creature
        def occupy(x, y):
            return x in range(0, size) and y in range(0, size)

        # If cell is adjacent to a creature
        def adjacent(x, y):
            return x in range(-1, size+1) and y in range(-1, size+1) and not occupy(x,y)

        def threaten_near(x, y):
            return x in range(-reach, size + reach) and y in range(-reach, size + reach)

        def threaten_far(x, y):
            return x in range(-far_reach, size + far_reach) and y in range(-far_reach, size + far_reach)

        self.block_size = 2 * far_reach + self.size
        self.offset = far_reach
        self.template = []

        for cx in range(-far_reach, size + far_reach):
            for cy in range(-far_reach, size + far_reach):
                t = 0
                if occupy(cx, cy):
                    t |= self.MARK_OCCUPY
                    self.tiles_occupied.append((cx, cy))
                elif threaten_near(cx, cy):
                    if self.near:
                        t |= self.MARK_THREATEN_NEAR
                        self.tiles_threatened.append((cx, cy))
                elif self.far and threaten_far(cx, cy):
                    t |= self.MARK_THREATEN_FAR
                    self.tiles_threatened.append((cx, cy))

                tile = (cx, cy, t)
                self.template.append(tile)
        pass

    def __str__(self):
        grid = []
        for x in range(0, self.block_size):
            grid.append([' '] * self.block_size)

        for tile in self.template:
            x, y, t = tile
            x += self.offset
            y += self.offset

            if t & self.MARK_THREATEN_NEAR:
                grid[x][y] = '+'
            if t & self.MARK_THREATEN_FAR:
                grid[x][y] = '*'
            if t & self.MARK_OCCUPY:
                grid[x][y] = 'X'
        result = ""
        for row in grid:
            row_str = "|" + ''.join(row) + "|\n"
            result += row_str
        return result



