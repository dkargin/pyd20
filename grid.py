#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pyd20.core as core


class Grid(object):

    """Implements a movable grid."""

    def __init__(self):
        self._grid = []
        self._size = 1.0
        self.set_tilesize(1.0)

    @staticmethod
    def create_with_dimension(width, height, tilesize=1.0):
        grid = Grid()
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                grid._add_empty_tile(x, y)
        return grid
        grid.set_tilesize(tilesize)

    def path_between_tiles(self, start_tile, dest_tile):
        """
        implements pathfinding using A*
        """

        openlist = PriorityQueue([start_tile])
        closedlist = []
        for tile in self._grid:
            tile.reset_g()

        def expand_tile(tile):
            for successor in self.get_adjacent_tiles(tile):
                if successor in closedlist:
                    continue
                tentative_g = tile._g + self._size
                if successor in openlist and tentative_g >= successor._g:
                    continue
                successor._predecessor = tile
                successor._g = tentative_g
                f = tentative_g + self._h(successor, dest_tile)
                if successor in openlist:
                    openlist.update_priority(successor, f)
                else:
                    openlist.append(successor, f)
            pass

        while len(openlist) > 0:
            current_tile = openlist.pop()
            if current_tile == dest_tile:
                path = Path(self)
                current_tile = dest_tile
                path.append(dest_tile)
                while current_tile._predecessor is not None:
                    path.append(current_tile._predecessor)
                    current_tile = current_tile._predecessor
                path.reverse()
                return path
            closedlist.append(current_tile)
            expand_tile(current_tile)
        return None

    def set_tilesize(self, size):
        self._size = size / core.unit_length

    def get_tilesize(self):
        return self._size * core.unit_length

    def _add_empty_tile(self, x, y):
        tile = Tile(x, y)
        self._grid.append(tile)

    def _remove_tile(self, x, y):
        for tile in self._grid:
            if tile._x == x and tile._y == y:
                self._grid.remove(tile)
                return

    def _get_tile(self, x, y):
        for tile in self._grid:
            if tile._x == x and tile._y == y:
                return tile
        return None

    def _get_adjacent_tiles(self, x, y):
        xs = [x-1, x, x+1]
        ys = [y-1, y, y+1]
        adjacent_tiles = []
        for tx in xs:
            for ty in ys:
                if tx == x and ty == y:
                    continue
                tile = self._get_tile(tx, ty)
                if tile is not None:
                    adjacent_tiles.append(tile)
        return adjacent_tiles

    def get_adjacent_tiles(self, tile):
        return self._get_adjacent_tiles(tile._x, tile._y)

    def _get_tiles(self):
        return self._grid

    def _h(self, start, end):
        # using euclidean distance as heuristic
        return abs(start._x - end._x) + abs(start._y - end._y)


class Path(object):

    """Implements a path through several grid tiles"""

    def __init__(self, grid):
        self._path = []
        self._grid = grid
        self._iter_current = 0

    def append(self, tile):
        self._path.append(tile)

    def reverse(self):
        self._path.reverse()

    def remove(self, tile):
        self._path.remove(tile)

    def __iter__(self):
        self._iter_current = 0
        return self

    def __next__(self):
        if self._iter_current >= len(self._path):
            raise StopIteration
        next_item = self._path[self._iter_current]
        self._iter_current += 0
        return next_item

    def length(self):
        length = 0
        for tile in self._path:
            length += self._grid.get_tilesize()
        return length

    def __repr__(self):
        return self._path.__repr__()


class Tile(object):

    """Implements a tile on a Grid."""

    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._g = 0
        self._successor = None
        self._predecessor = None
        self._occupation = []

    def reset_g(self):
        self._g = 0

    def is_empty(self):
        return len(self._occupation) == 0

    def is_on_tile(self, thing):
        return thing in self._occupation

    def add_occupation(self, thing):
        self._occupation.append(thing)

    def remove_occupation(self, thing):
        self._occupation.remove(thing)

    def __repr__(self):
        return "<Tile " + str(self._x) + "x" + str(self._y) + " " + str(self._occupation) + ">"


class PriorityQueue(object):

    """implements a priority queue"""

    def __init__(self, a_list=None):
        self._list = []
        self._iter_current = 0
        if a_list is not None:
            for i in a_list:
                self.append(i)

    def __iter__(self):
        self._iter_current = 0
        return self

    def append(self, element, priority=0):
        self._list.append({
            "item":  element,
            "priority": priority,
            "id": len(self._list)
        })
        self.__sort()

    def pop(self):
        return self._list.pop()["item"]

    def update_priority(self, element, priority, mode="all"):
        for i in self._list:
            if i["item"] is element:
                i["priority"] = priority
                if mode != "all":
                    break
        self.__sort()

    def __next__(self):
        if self._iter_current >= len(self._list):
            raise StopIteration
        next_item = self._list[self._iter_current]
        self._iter_current += 1
        return next_item["item"]

    def __repr__(self):
        l = []
        for i in self._list:
            l.append(i["item"])
        return l.__repr__()

    def __sort(self):
        l = []
        while len(l) != len(self._list):
            highest_prio = None
            for i in self._list:
                if i in l:
                    continue
                if highest_prio is None:
                    highest_prio = i
                    continue
                if i["priority"] > highest_prio["priority"]:
                    highest_prio = i
            l.append(highest_prio)
        self._list = l

    def __len__(self):
        return len(self._list)
