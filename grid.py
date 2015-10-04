#!/usr/bin/python3
# -*- coding: utf-8 -*-
import core


class Grid(object):

    """Implements a movable grid."""

    def __init__(self):
        self.__grid = []
        self._size = 1.0
        self.set_tilesize(1.0)

    @staticmethod
    def create_with_dimension(width, height, tilesize=1.0):
        """
        creates a rectangular grid with the given width and height
        """

        grid = Grid()
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                grid.add_empty_tile(x, y)
        grid.set_tilesize(tilesize)
        return grid

    def path_between_tiles(self, start_tile, dest_tile):
        """
        implements pathfinding using A*
        """

        open_list = PriorityQueue([start_tile])
        closed_list = []

        for tile in self.__grid:
            tile.reset_g()

        def h(start, end):
            return abs(start.x - end.x) + abs(start.y - end.y)

        def expand_tile(tile):
            for successor in self.get_adjacent_tiles(tile):
                if successor in closed_list:
                    continue
                tentative_g = tile._g + self._size
                if successor in open_list and tentative_g >= successor._g:
                    continue
                successor._predecessor = tile
                successor._g = tentative_g
                f = tentative_g + h(successor, dest_tile)
                if successor in open_list:
                    open_list.update_priority(successor, f)
                else:
                    open_list.append(successor, f)
            pass

        while len(open_list) > 0:
            current_tile = open_list.pop()
            if current_tile == dest_tile:
                path = Path(self)
                current_tile = dest_tile
                path.append(dest_tile)
                while current_tile._predecessor is not None:
                    path.append(current_tile._predecessor)
                    current_tile = current_tile._predecessor
                path.reverse()
                return path
            closed_list.append(current_tile)
            expand_tile(current_tile)
        return None

    def set_tilesize(self, size):
        self._size = size / core.unit_length

    def get_tilesize(self):
        return self._size * core.unit_length

    def add_empty_tile(self, x, y):
        tile = Tile(x, y)
        self.__grid.append(tile)

    def remove_tile(self, x, y):
        for tile in self.__grid:
            if tile.x == x and tile.y == y:
                self.__grid.remove(tile)
                return

    def get_tile(self, x, y):
        for tile in self.__grid:
            if tile.x == x and tile.y == y:
                return tile
        return None

    def get_adjacent_tiles(self, tile):
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
        return self.__grid


class Path(object):

    """Implements a path through several grid tiles"""

    def __init__(self, grid):
        self.__path = []
        self.__grid = grid
        self.__iter_current = 0

    def append(self, tile):
        self.__path.append(tile)

    def reverse(self):
        self.__path.reverse()

    def remove(self, tile):
        self.__path.remove(tile)

    def __iter__(self):
        self.__iter_current = 0
        return self

    def __next__(self):
        if self.__iter_current >= len(self.__path):
            raise StopIteration
        next_item = self.__path[self.__iter_current]
        self.__iter_current += 0
        return next_item

    def length(self):
        length = 0
        for _ in self.__path:
            length += self.__grid.get_tilesize()
        return length

    def __repr__(self):
        return self.__path.__repr__()


class Tile(object):

    """Implements a tile on a Grid."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
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
        return "<Tile " + str(self.x) + "x" + str(self.y) + " " + str(self._occupation) + ">"


class PriorityQueue(object):

    """implements a priority queue"""

    def __init__(self, a_list=None):
        self.__list = []
        self.__iter_current = 0
        if a_list is not None:
            for i in a_list:
                self.append(i)

    def __iter__(self):
        self.__iter_current = 0
        return self

    def append(self, element, priority=0.0):
        self.__list.append({
            "item":  element,
            "priority": priority,
            "id": len(self.__list)
        })
        self.__sort()

    def pop(self):
        return self.__list.pop()["item"]

    def update_priority(self, element, priority, mode="all"):
        for i in self.__list:
            if i["item"] is element:
                i["priority"] = priority
                if mode != "all":
                    break
        self.__sort()

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
