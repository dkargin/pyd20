import heapq
import math

from .grid import *
from .entity import *


# Default cost function for pathfinder
def default_cost(src, dst):
    return math.sqrt((src.x - dst.x) ** 2 + (src.y - dst.y) ** 2)


# Does pathfinding stuff
class PathFinder(object):

    class Node:
        """
        Node for search tree
        """
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self._g = 0
            self._h = 0
            self._lh = 0
            self._predecessor = None
            self._pathstate = 0
            self._target_mark = 0

        def __lt__(self, other):
            return self._g < other._g

        def __hash__(self):
            return id(self)

    def __init__(self, grid, objsize = 1):
        self.grid = grid
        self.open_list = []
        self.search_index = 0
        self._objsize = 1
        self._occupation = []

        self._revision = grid.revision - 1

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
        # Contains distance transform result
        self._distance = [0] * size

    # Search PF node by a coordinates
    def get_tile_node(self, x, y):
        return self._node_index[x + y * self._width]

    # Update local obstacle map
    def sync_grid(self, grid):
        if self._revision == grid.revision:
            return
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
            if not tile.is_empty():
                cost += 5

            self._costmap[index] = cost
            index += 1

        self._revision = grid.revision

    # TODO: should move costmap to cython
    def sum_obstacle(self, x0, y0):
        cost = 0
        for adj in self._occupation:
            index = x0 + adj[0] + (y0+adj[1])*self._width
            cost += self._costmap[index]
        return cost

    def _get_node(self, x, y):
        index = x + y*self._width;
        node = self._node_index[index]
        if node is None:
            self._node_index[index] = node = PathFinder.Node(x,y)
        return node

    # Check if coordinates are valid for creature and it is is inside the map
    def is_inside(self, x, y):
        return x in range(0, self._width - self._objsize + 1) and y in range(0, self._height - self._objsize + 1)

    # Iterates adjacent cells
    def _get_adjacent(self, src, x, y):
        def check_adjacent(x, y, base):
            if self.is_inside(x, y) and self.sum_obstacle(x, y) == 0:
                return self._get_node(x, y), base

        moves = [check_adjacent(x+1, y, 5),
                 check_adjacent(x-1, y, 5),
                 check_adjacent(x, y+1, 5),
                 check_adjacent(x, y-1, 5)]
        # Allow diagonals
        if moves[0] is not None and moves[2] is not None:
            moves.append(check_adjacent(x + 1, y + 1, 7))

        if moves[0] is not None and moves[3] is not None:
            moves.append(check_adjacent(x + 1, y - 1, 7))

        if moves[1] is not None and moves[2] is not None:
            moves.append(check_adjacent(x - 1, y + 1, 7))

        if moves[1] is not None and moves[3] is not None:
            moves.append(check_adjacent(x - 1, y - 1, 7))

        for move in moves:
            if move is not None:
                yield move

    def expand_tile(self, tile, costfn = default_cost):
        """
        :param tile:
        :param costfn: function for calculating tile cost
        :return:
        """
        # Check diagonals
        for next, cellcost in self._get_adjacent(tile, tile.x, tile.y):
            # Skip nodes that are already visited
            if next._pathstate == self.search_index:
                continue
            next._g = tile._g + costfn(tile, next) + cellcost
            next._predecessor = tile
            self.push_node(next)
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
        path.append(Point(x=current_node.x, y=current_node.y))
        while current_node._predecessor is not None:
            current_node = current_node._predecessor
            if current_node != start:
                path.append(Point(x=current_node.x, y=current_node.y))

        # Flipping back reversed path
        path.reverse()
        return path

    def get_wave_index(self):
        return self.search_index

    def get_target_index(self):
        return self.search_index+1

    def run_wave(self, start_node, finish_check):
        start_node._g = 0
        start_node._predecessor = None
        self.open_list = []
        self.push_node(start_node)

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

    def path_to_melee_range(self, start_pos, dest, range0, range1):
        self.sync_grid(self.grid)
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
        tiles_near = get_coord_range(dest, range0)
        tiles_far = get_coord_range(dest, range1)
        for tile in tiles_far:
            if tile in tiles_near:
                continue
            node = self._get_node(*tile)
            if node is not None:
                node._target_mark = self.get_target_index()

        start_node = self._get_node(start_pos.x, start_pos.y)

        return self.run_wave(start_node, lambda x: x._target_mark == self.get_target_index())

    def path_between_tiles(self, start_tile, dest_tile):
        self.sync_grid(self.grid)
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
