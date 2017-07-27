import heapq
import math

from .grid import *
from .entity import *


# Default cost function for pathfinder
def default_cost(src, dst):
    return math.sqrt((src.x - dst.x) ** 2 + (src.y - dst.y) ** 2)


# Does pathfinding stuff
class PathFinder(object):

    class Node(Point):
        """
        Node for search tree
        """
        def __init__(self, x, y):
            super(PathFinder.Node, self).__init__(x=x, y=y)
            self.g = 0
            self.h = 0
            self._lh = 0
            self.predecessor = None
            self.pathstate = 0
            self.target_mark = 0

        def __lt__(self, other):
            return self.g < other.g

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
        for ax, ay in self._occupation:
            index = x0 + ax + (y0 + ay)*self._width
            cost += self._costmap[index]
        return cost

    def _get_node(self, x, y):
        index = x + y*self._width
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

    def expand_tile(self, tile, costfn=default_cost):
        """
        :param tile:
        :param costfn: function for calculating tile cost
        :return:
        """
        # Check diagonals
        for adjacent, cell_cost in self._get_adjacent(tile, tile.x, tile.y):
            # Skip nodes that are already visited
            if adjacent.pathstate == self.search_index:
                continue
            adjacent.g = tile.g + costfn(tile, adjacent) + cell_cost
            adjacent.predecessor = tile
            self.push_node(adjacent)
        pass

    def push_node(self, node):
        node.pathstate = self.get_wave_index()
        heapq.heappush(self.open_list, (node.g, node))

    def pop_node(self):
        return heapq.heappop(self.open_list)[1]

    # Compile path
    def compile_path(self, start):
        path = Path(self.grid)
        # Building reversed path
        current_node = start
        while current_node.predecessor is not None:
            path.append(Point(x=current_node.x, y=current_node.y))
            current_node = current_node.predecessor

        # Flipping back reversed path
        path.reverse()
        return path

    def get_wave_index(self):
        return self.search_index

    def get_target_index(self):
        return self.search_index+1

    def run_wave(self, start_node, finish_check):
        start_node.g = 0
        start_node.predecessor = None
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

    def path_to_range(self, start_pos, dest, range):
        self.sync_grid(self.grid)
        """
        :param start_pos:Point starting position
        :param dest:Point
        :param range:float desired range
        :return:Path
        """
        pt = Point()

        def in_range(node):
            pt.x = node.x
            pt.y = node.y
            return node.distance(pt) <= range
        start_node = self._get_node(start_pos.x, start_pos.y)

        # Run wave and compile the path
        return self.run_wave(start_node, in_range)

    # Drawing a straight path for charge attacks
    def check_straight_path(self, start_pos, dest):
        self.sync_grid(self.grid)
        # There are obstacles that are created by the unit itself
        # Pathfinder breaks into this obstacles
        line_path = get_line(start_pos.tuple(), dest.tuple())
        limit = 0
        path = Path(self.grid)
        sum_obstacles = 0
        for x, y in line_path:
            move_cost = self.sum_obstacle(x, y)
            if move_cost > limit:
                return None
            path.append(Point(x=x,y=y))
            sum_obstacles += move_cost
        # Flipping back reversed path
        path.reverse()
        return path

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
                node.target_mark = self.get_target_index()

        start_node = self._get_node(start_pos.x, start_pos.y)
        # Run wave and compile the path
        return self.run_wave(start_node, lambda x: x.target_mark == self.get_target_index())

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

    class Iterator:
        def __init__(self, path):
            self._path = path
            self._index = 0

        def next(self):
            return self.__next__()

        def __next__(self):
            if self._index >= len(self._path):
                raise StopIteration
            next_item = self._path[self._index]
            self._index += 1
            return next_item

    def __getitem__(self, index):
        return self.__path[index]

    def __len__(self):
        return len(self.__path)

    def __iter__(self):
        return Path.Iterator(self)

    def __repr__(self):
        return self.__path.__repr__()
