import core
import random
import heapq
import math


TERRAIN_FREE = 0
TERRAIN_WALL = 1


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
        self.set_tilesize(5.0)
        self._width = width
        self._height = height
        self.__grid = []

        # Maps tuple (size, reach, near, far) -> OccupancyTemplate
        self._occupancy_templates = {}

        for y in range(0, height):
            for x in range(0, width):
                self.__grid.append(Tile(x,y))

    def set_tilesize(self, size):
        """
        sets the tilesize in the current unit

        :param float size: the new tilesize
        """
        self._size = size / core.unit_length

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_tilesize(self):
        """
        returns the tilesize in the current unit

        :rtype: int
        """
        return self._size * core.unit_length

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
            return (tile.x, tile.y)
        else:
            return None

    def get_tile_range(self, center, distance, skip_center = False):
        """
        :param center: - center tile
        :param distance: - tile range
        :return: [] array of selected tiles
        """
        tiles = []
        for y in range(center.y - distance, center.y + distance + 1):
            for x in range(center.x - distance, center.x + distance + 1):
                tile = self.get_tile(x,y)
                if skip_center and tile.x == center.x and tile.y == center.y:
                    continue
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
            template = self.get_occupancy_template(entity.get_size(), entity.natural_reach(), entity.has_reach_near(), entity.has_reach_far())
            entity.set_occupation_template(template)

        def offset_tile(coord) -> Tile:
            return self.get_tile(coord[0] + entity.x, coord[1] + entity.y)

        # Occupying tiles
        for offset in template.tiles_occupied:
            tile = offset_tile(offset)
            if tile is not None and entity not in tile.occupation:
                tile.occupation.append(entity)
                if tile not in entity._occupied_tiles:
                    entity._occupied_tiles.append(tile)

        # Mark threatened area
        for offset in template.tiles_threatened:
            tile = offset_tile(offset)
            if tile is not None and entity not in tile.threaten:
                tile.threaten.append(entity)
                if tile not in entity._threatened_tiles:
                    entity._threatened_tiles.append(tile)

    # Remove entity from grid.
    # Removes all the references, and tile threatening as well
    def unregister_entity(self, entity):
        for tile in entity._threatened_tiles:
            tile.threaten.remove(entity)
        entity._threatened_tiles = []

        for tile in entity._occupied_tiles:
            tile.occupation.remove(entity)
        entity._occupied_tiles = []



    # Set terrain type for a tile
    def set_terrain(self, x, y, type):
        tile = self.get_tile(x,y)
        tile.set_terrain(type)

    # Get tile reference
    def get_tile(self, x, y):
        """
        returns the tile at position x/y

        :param int x: the x coordinate of the tile
        :param int y: the y coordinate of the tile
        :rtype: Tile
        """
        if self.is_inside(x,y):
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
    def get_occupancy_template(self, size, base_reach, near, far):
        key = (size, base_reach, near, far)

        if key in self._occupancy_templates:
            return self._occupancy_templates(key)

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
    :type _g: int Pathfinder stuff
    :type _successor: Tile | None
    :type _predecessor: Tile | None
    :type _occupation: list
    """

    def __init__(self, x, y):
        """
        Creates a Tile object
        :param int x: The x position of the Tile
        :param int y: The y position of the Tile
        """
        self.x = x
        self.y = y
        self._g = 0
        # Do we need to store pathfinding info right here?
        # Let it be for now
        self._successor = None
        self._predecessor = None
        self.occupation = []
        self.terrain = TERRAIN_FREE
        # Pathfinder search index
        self._pathstate = 0
        self._target_mark = 0
        # Objects that threaten this tile
        self.threaten = []

    def is_empty(self):
        """
        returns whether the Tile is occupied or not

        :rtype: bool
        """
        return len(self.occupation) == 0 and self.terrain == TERRAIN_FREE

    def coords(self):
        return (self.x, self.y)

    def set_terrain(self, type):
        self.terrain = type

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

    def reset_g(self):
        """
        auxiliary method used for pathfinding. resets calculated g value
        """
        self._g = 0

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._g < other._g

    def __hash__(self):
        return id(self)


# Default cost function for pathfinder
def default_cost(src, dst):
    return math.sqrt((src.x - dst.x) ** 2 + (src.y - dst.y) ** 2)


# Does pathfinding stuff
class PathFinder(object):
    def __init__(self, grid):
        self.grid = grid
        self.open_list = []
        self.search_index = 0

    def expand_tile(self, tile, costfn = default_cost):
        """
        :param tile:
        :param costfn: function for calculating tile cost
        :return:
        """
        adjacent = self.grid.get_adjacent_tiles(tile)
        for next in adjacent:
            if not next.is_empty():
                continue
            # Skip nodes that are already visited
            if next._pathstate == self.search_index:
                continue
            next._g = tile._g + costfn(tile, next)
            next._predecessor = tile
            self.push_node(next)
            #self.open_list.append(next, next._g)
        pass

    def push_node(self, tile):
        tile._pathstate = self.get_wave_index()
        heapq.heappush(self.open_list, (tile._g, tile))

    def pop_node(self):
        return heapq.heappop(self.open_list)[1]

    # Compile path
    def compile_path(self, start):
        path = Path(self.grid)
        # Building reversed path
        current_tile = start
        path.append(start)
        while current_tile._predecessor is not None:
            current_tile = current_tile._predecessor
            if current_tile != start:
                path.append(current_tile)
        # Flipping back reversed path
        path.reverse()
        return path

    def path_to(self, start_tile, dest_functor):
        self.search_index += 2

        start_tile._g = 0
        start_tile._predecessor = None
        self.open_list = []
        self.push_node(start_tile)

        iteration = 0

        while len(self.open_list) > 0:
            # cost, current_tile = self.open_list.pop()
            cost, current_tile = heapq.heappop(self.open_list)
            if dest_functor(current_tile):
                return self.compile_path(current_tile)

            self.expand_tile(current_tile)
            iteration += 1
        return None

    def get_wave_index(self):
        return self.search_index

    def get_target_index(self):
        return self.search_index+1

    def path_to_range(self, start_tile, dest_tile, range):
        """
        Calculate path to any tile in range of dest_tile
        :param start_tile: starting tile
        :param dest_tile: destination tile
        :param range: minimal range to achieve
        :return:
        """
        self.search_index += 2
        # Mark destination tiles
        target_tiles = self.grid.get_tile_range(dest_tile, range)
        for tile in target_tiles:
            tile._target_mark = self.get_target_index()

        start_tile._g = 0
        start_tile._predecessor = None
        # self.open_list = PriorityQueue([start_tile])
        self.open_list = []
        self.push_node(start_tile)

        iteration = 0

        while len(self.open_list) > 0:
            # cost, current_tile = self.open_list.pop()
            cost, current_tile = heapq.heappop(self.open_list)
            # Check if we have reached our destination
            if current_tile._target_mark == self.get_target_index():
                return self.compile_path(current_tile)

            self.expand_tile(current_tile)
            iteration += 1
        return None

    def path_between_tiles(self, start_tile, dest_tile):
        """
        Get direct path between tiles
        Implemented pathfinding using A*

        :rtype: Path
        """

        self.search_index += 2

        start_tile._g = 0
        start_tile._predecessor = None

        self.open_list = []
        self.push_node(start_tile)

        iteration = 0

        while len(self.open_list) > 0:
            #cost, current_tile = self.open_list.pop()
            cost, current_tile = heapq.heappop(self.open_list)
            if current_tile == dest_tile:
                return self.compile_path(current_tile)

            self.expand_tile(current_tile)
            iteration += 1
        return None


class Path(object):
    """
    Implements a path through several grid tiles

    :type __path: Tile[]
    :type __grid: Grid
    :type __iter_current: int
    """

    def __init__(self, grid):
        """
        Creates a Path object.

        :param Grid grid: Reference to the grid of the path
        """
        self.__path = []
        self.__grid = grid
        self.__iter_current = 0

    def get_path(self):
        return self.__path

    def first(self):
        """
        Returns the first tile in the path

        :rtype: Tile
        """
        return self.__path[0]

    def last(self):
        """
        Returns the last tile in the path

        :rtype: Tile
        """
        return self.__path[len(self.__path) - 1]

    def append(self, tile):
        """
        append tile to the path

        :param Tile tile: the tile to append
        """
        self.__path.append(tile)

    def reverse(self):
        """
        reverse the path
        """
        self.__path.reverse()

    def remove(self, tile):
        """
        remove a tile from the path

        :param Tile tile: the tile to remove
        """
        self.__path.remove(tile)

    def length(self):
        """
        returns the length of the path in the current unit

        :rtype: float
        """
        length = 0
        for _ in self.__path:
            length += self.__grid.get_tilesize()
        return length

    def count(self):
        """
        returns number of waypoints in the path
        :return: int
        """
        return len(self.__path)

    def __getitem__(self, index):
        return self.__path[index]

    def __iter__(self):
        self.__iter_current = 0
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.__iter_current >= len(self.__path):
            raise StopIteration
        next_item = self.__path[self.__iter_current]
        self.__iter_current += 0
        return next_item

    def __repr__(self):
        return self.__path.__repr__()


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


        def classify(self, x, y):
            return False

        # Returns if cell is occupied by this creature
        def occupy(x, y):
            return x in range(0, size) and y in range(0, size)

        # If cell is adjacent to a creature
        def adjacent(x, y):
            return x in range(-1, size+1) and y in range(-1, size+1) and not occupy(x,y)

        def threaten_near(x, y):
            return x in range(-reach, size + reach) and y in range(-reach, size + reach)

        def threaten_far(x,y):
            return x in range(-far_reach, size + far_reach) and y in range(-far_reach, size + far_reach)

        self.block_size = 2 * far_reach + self.size
        self.offset = far_reach
        self.template = []

        for x in range(-far_reach, size + far_reach):
            for y in range(-far_reach, size + far_reach):
                type = 0
                if occupy(x,y):
                    type |= self.MARK_OCCUPY
                    self.tiles_occupied.append((x, y))
                elif threaten_near(x,y):
                    if self.near:
                        type |= self.MARK_THREATEN_NEAR
                        self.tiles_threatened.append((x,y))
                elif self.far and threaten_far(x,y):
                    type |= self.MARK_THREATEN_FAR
                    self.tiles_threatened.append((x, y))

                tile = (x, y, type)
                self.template.append(tile)
        pass

    def __str__(self):
        grid = []
        for x in range(0, self.block_size):
            grid.append([' '] * self.block_size)

        for tile in self.template:
            x,y,type = tile
            x += self.offset
            y += self.offset

            if type & self.MARK_THREATEN_NEAR:
                grid[x][y] = '+'
            if type & self.MARK_THREATEN_FAR:
                grid[x][y] = '*'
            if type & self.MARK_OCCUPY:
                grid[x][y] = 'X'
        result = ""
        for row in grid:
            row_str = "|" + ''.join(row) + "|\n"
            result += row_str
        return result

    """
    def __repr__(self):
        return str(self)
    """


