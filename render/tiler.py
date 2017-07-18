import pygame
from sim.grid import *


# Tile generation rules

# Get cross-adjacent tiles
def cross(x, y):
    yield (x-1, y)
    yield (x+1, y)
    yield (x, y+1)
    yield (x, y-1)


def surrounded(validator):
    def check(x0, y0, access):
        for (x, y) in cross(x0,y0):
            if not validator(access(x,y)):
                return False
        return True
    return check


# Tile validator
def always_true(x,y, access): return True


# Suits one tile type
def valid_one(t): return lambda other: other == t


# Suit two tile types
def valid_two(t0, t1): return lambda other: (other == t0 or other == t1)


# Get cross-corner tiles
def corner(x, y, hor, ver):
    yield (x - 1, y) if hor else (x + 1, y)
    yield (x, y - 1) if ver else (x, y + 1)


def check_corner(validator, hor, ver):
    def check(x, y, access):
        for (x,y) in corner(x,y, hor, ver):
            if not validator(access(x, y)) :
                return False
        return True
    return check


def up_down(up, down):
    def check(x, y, access):
        return up(access(x, y-1)) and down(access(x, y+1))
    return check


def top_3(*types):
    def check(x, y, access):
        return types[0](access(x-1, y-1)) and types[1](access(x, y-1)) and types[2](access(x+1, y-1))
    return check


def left_3(*args): return lambda x, y, a: args[0](a(x-1, y-1)) and args[1](a(x-1, y)) and args[2](a(x-1, y+1))


def right_3(*args): return lambda x, y, a: args[0](a(x+1, y-1)) and args[1](a(x+1, y)) and args[2](a(x+1, y+1))


def left(check): return lambda x, y, a: check(a(x-1, y))


def right(check): return lambda x, y, a: check(a(x+1, y))


def top(t):
    def check(x, y, access):
        return t(access(x, y-1))
    return check

any_free = valid_two(TERRAIN_FREE, TERRAIN_GRASS)
any_wall = valid_one(TERRAIN_WALL)

tile_rules = {
    TERRAIN_FREE: [(7, 1, top_3(valid_one(TERRAIN_WALL), valid_one(TERRAIN_WALL), valid_one(TERRAIN_WALL))),
                   (6, 1, top_3(any_free, any_wall, any_wall)),
                   (8, 1, top_3(any_wall, any_wall, any_free)),
                   (9, 0, always_true)],


    TERRAIN_GRASS: [(9, 1, always_true)],
    TERRAIN_WALL: [(6, 0, check_corner(any_free, True, True)),
                   (8, 0, check_corner(any_free, False, True)),
                   (8, 0, check_corner(any_free, False, True)),
                   (0, 1, left(any_free)),
                   (2, 1, right(any_free)),
                   (7, 0, top(any_free))]
}


class Tiler:
    def __init__(self, width, height, size, path):
        """
        :param width: - grid width
        :param height: - grid height
        :param size: - tile size
        :param path: - path to tileset image
        """
        self.width = width
        self.height = height
        self._size = size
        self._picked_tiles = [None] * width * height
        self.surface = pygame.image.load(path)
        self._ready = False

    # Updates current tile set
    def update(self, grid):
        if self._ready == True:
            return
        def access(x, y):
            tile = grid.get_tile(x, y)
            if tile is None:
                return TERRAIN_OUTSIDE
            return tile.terrain

        for tile in grid.get_tiles():
            if tile.terrain in tile_rules:
                for (tx, ty, rule) in tile_rules[tile.terrain]:
                    if rule(tile.x, tile.y, access):
                        self._use_tile(tile.x, tile.y, tx, ty)
                        break
            #self._process_tile(tile, access)

        self._ready = True

    # Update assigned tile
    def _use_tile(self, x, y, tx, ty):
        self._picked_tiles[x + y*self.width] = self.tile_rect(tx, ty)

    def draw_tile(self, surface, dst, index):
        src_rect = self._picked_tiles[index]
        if src_rect is None:
            return
        surface.blit(self.surface, dst, area=src_rect)

    def tile_rect(self, x, y):
        return x * self._size, y * self._size, self._size, self._size
