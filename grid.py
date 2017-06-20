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


def default_cost(src, dst):
    return math.sqrt((src.x-dst.x)**2 + (src.y - dst.y)**2)

# Does pathfinding stuff
class PathFinder(object):
    def __init__(self, grid):
        self.grid = grid
        self.open_list = []
        #self.closed_list = []
        self.search_index = 0

    def expand_tile(self, tile, costfn = default_cost):
        """
        :param tile:
        :param costfn: function for calculating tile cost
        :return:
        """
        adjacent = self.grid.get_adjacent_tiles(tile)
        for next in adjacent:
            # Skip nodes that are already visited
            if next._pathstate == self.search_index:
                continue
            next._g = tile._g + costfn(tile, next)
            next._predecessor = tile
            next._pathstate = self.search_index
            self.push_node(next)
            #self.open_list.append(next, next._g)
        pass

    def push_node(self, tile):
        heapq.heappush(self.open_list, (tile._g, tile))

    def pop_node(self):
        return heapq.heappop(self.open_list)[1]

    def path_between_tiles(self, start_tile, dest_tile):
        """
        implements pathfinding using A*

        :rtype: Path
        """

        self.search_index += 1

        start_tile._pathstate = self.search_index
        start_tile._g = 0
        start_tile._predecessor = None

        #self.open_list = PriorityQueue([start_tile])
        self.open_list = []
        self.push_node(start_tile)

        iteration = 0

        while len(self.open_list) > 0:
            #cost, current_tile = self.open_list.pop()
            cost, current_tile = heapq.heappop(self.open_list)
            if current_tile == dest_tile:
                path = Path(self.grid)
                current_tile = dest_tile
                path.append(dest_tile)
                while current_tile._predecessor is not None:
                    current_tile = current_tile._predecessor
                    if current_tile != start_tile:
                        path.append(current_tile)
                path.reverse()
                return path
            self.expand_tile(current_tile)
            iteration += 1
        return None


class Tile(object):
    """
    Implements a tile on a Grid.

    :type x: int
    :type y: int
    :type _g: int
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
        self._occupation = []
        self._terrain = TERRAIN_FREE
        # Pathfinder search index
        self._pathstate = 0
        # Objects that threaten this tile
        self._threaten = []

    def is_empty(self):
        """
        returns whether the Tile is occupied or not

        :rtype: bool
        """
        return len(self._occupation) == 0 and self._terrain == TERRAIN_FREE

    def has_occupation(self, thing):
        """
        returns whether the thing occupies this tile or not

        :param thing: the thing to check
        :rtype: bool
        """
        return thing in self._occupation

    def is_threatened(self, combatant):
        if len(self._threaten) == 0:
            return False
        return True

    def add_occupation(self, thing):
        """
        make a thing occupy this tile. Multiple occupations are possible.

        :param thing: the thing to occupy this tile
        """
        self._occupation.append(thing)

    def remove_occupation(self, thing):
        """
        end a things occupation of this tile.

        :param thing: the thing to free from this tile
        """
        self._occupation.remove(thing)

    def __repr__(self):
        return "<Tile " + str(self.x) + "x" + str(self.y) + " " + str(self._occupation) + ">"

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




class PriorityQueue(object):

    """
    implements a priority queue. This class is primarily used as an auxiliary class for the pathfinding

    :type __list: list
    :type __iter_current: int
    """

    def __init__(self, a_list=None):
        """
        Creates a PriorityQueue object. Initial items in the list have priority 0.

        :param list a_list: Initial items in the list.
        """
        self.__list = []
        self.__iter_current = 0
        if a_list is not None:
            for i in a_list:
                self.append(i)

    def __iter__(self):
        self.__iter_current = 0
        return self

    def append(self, element, priority=0.0):
        """
        append an element to the list

        :param element: The element to append
        :param priority: The priority of the element
        """
        self.__list.append({
            "item":  element,
            "priority": priority,
            "id": len(self.__list)
        })
        self.__sort()

    def pop(self):
        """
        removes and returns the element with the highest priority

        :rtype: any
        """
        return self.__list.pop()["item"]

    def update_priority(self, element, priority, mode="all"):
        """
        updates the priority of an item in the queue. if an element has multiple occurrences in the queue,
        the priority of the elements is updated depending on the mode. "all" changes the priority of all
        elements in the queue, "first" changes only the first occurrence. "all" is the default behaviour.

        :param element: The element to change the priority for
        :param int priority: The priority value
        :param str mode: The update-mode. Possible values are: "all" (default), "first"
        """
        for i in self.__list:
            if i["item"] is element:
                i["priority"] = priority
                if mode != "all":
                    break
        self.__sort()

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.__iter_current >= len(self.__list):
            raise StopIteration
        next_item = self.__list[self.__iter_current]
        self.__iter_current += 1
        return next_item["item"]

    def __repr__(self):
        l = []
        for i in self.__list:
            l.append(i["item"])
        return l.__repr__()

    def __sort(self):
        l = []
        while len(l) != len(self.__list):
            highest_prio = None
            for i in self.__list:
                if i in l:
                    continue
                if highest_prio is None:
                    highest_prio = i
                    continue
                if i["priority"] > highest_prio["priority"]:
                    highest_prio = i
            l.append(highest_prio)
        self.__list = l

    def __len__(self):
        return len(self.__list)


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
