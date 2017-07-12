import heapq
import math

from .grid import *


# Default cost function for pathfinder
def default_cost(src, dst):
    return math.sqrt((src.x - dst.x) ** 2 + (src.y - dst.y) ** 2)


# Does pathfinding stuff
class PathFinder(object):

    class Node:
        """
        Node for search tree
        """
        def __init__(self):
            self.g = 0
            self.h = 0
            self.lh = 0
            self.predecessor = None
            self.pathstate = 0

    def __init__(self, grid, objsize = 1):
        self.grid = grid
        self.open_list = []
        self.search_index = 0
        self._objsize = 1
        self._occupation = []
        for y in range(0, self._objsize*2-1):
            for x in range(0, self._objsize * 2 - 1):
                self._occupation.append((x, y))

        size = grid.get_width()*grid.get_height()

        self._width = grid.get_width()
        self._height = grid.get_height()
        # Node index
        self._node_index = [None] * size
        # Costs for each tile
        self._costmap = [0] * size

    # Search PF node by a coordinates
    def get_tile_node(self, x, y):
        return self._node_index[x + y * self._width]

    # Update local obstacle map
    def sync_grid(self, grid):
        self._width = grid.get_width()
        self._height = grid.get_height()
        size = grid.get_width() * grid.get_height()
        if len(self._costmap) != size:
            print('Map size has changed to %dx%d' % (self._width, self._height))
            self._costmap = [0] * size

        index = 0
        for tile in grid.get_tiles():
            terrain = tile.terrain
            cost = 0
            if terrain == TERRAIN_WALL:
                cost += 100

            self._costmap[index] = cost
            index += 1

    # TODO: implement it in cython
    def sum_obstacle(self, x0, y0):
        cost = 0
        for adj in self._occupation:
            index = x0 + x0 + (y0+adj[1])*self._width
            cost += self._costmap[index]

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

    def push_node(self, node):
        node._pathstate = self.get_wave_index()
        heapq.heappush(self.open_list, (node._g, node))

    def pop_node(self):
        return heapq.heappop(self.open_list)[1]

    # Compile path
    def compile_path(self, start):
        path = Path(self.grid)
        # Building reversed path
        current_node = start
        path.append(start)
        while current_node._predecessor is not None:
            current_node = current_node._predecessor
            if current_node != start:
                path.append(current_node)
        # Flipping back reversed path
        path.reverse()
        return path

    def get_wave_index(self):
        return self.search_index

    def get_target_index(self):
        return self.search_index+1

    def run_wave(self, start_tile, finish_check):
        start_tile._g = 0
        start_tile._predecessor = None
        self.open_list = []
        self.push_node(start_tile)

        iteration = 0

        while len(self.open_list) > 0:
            # cost, current_tile = self.open_list.pop()
            cost, current_tile = heapq.heappop(self.open_list)
            # Check if we have reached our destination
            if finish_check(current_tile):
                return self.compile_path(current_tile)

            self.expand_tile(current_tile)
            iteration += 1
        return None

    def path_to_melee_range(self, start_tile, dest, range0, range1):
        """
        Calculate path to any tile in range of dest_tile
        :param start_tile: starting tile
        :param dest_tile: destination tile
        :param range: minimal range to achieve
        :return:
        """
        self.search_index += 2
        if range0 > range1:
            tmp = range0
            range0 = range1
            range1 = tmp
        # Mark destination tiles
        tiles_near = self.grid.get_tile_range(dest, range0)
        tiles_far = self.grid.get_tile_range(dest, range1)
        for tile in tiles_far:
            if tile in tiles_near:
                continue
            tile._target_mark = self.get_target_index()

        return self.run_wave(start_tile, lambda x: x._target_mark == self.get_target_index())

    def path_between_tiles(self, start_tile, dest_tile):
        """
        Get direct path between tiles
        :rtype: Path
        """
        self.search_index += 2
        return self.run_wave(start_tile, lambda x: x == dest_tile)


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
