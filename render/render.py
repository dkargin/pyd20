import pygame
import math
from battle.combatant import Combatant
from battle.grid import *
from .tiler import Tiler

# Pixel size for a tile
TILESIZE=32

# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GREY0 = ( 64,  64,  64)
GREY1 = (128, 128, 128)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
GREEN0 = (  16, 128,  16)
BLUE  = (  0,   0, 255)


class Renderer:
    class Sprite:
        """
        Wrapper for surface object
        """
        def __init__(self, coord, surface):
            self.coord = coord
            self.surface = surface

    def __init__(self, battle, offset=0):
        pygame.init()
        grid = battle.grid
        self._tiler = Tiler(grid.get_width(), grid.get_height(), 32, 'data/peasanttiles02.png')
        self.grid_top = offset
        self.grid_left = offset

        self.screen_width = grid.get_width() * TILESIZE + 2 * offset
        self.screen_height = grid.get_height() * TILESIZE + 2 * offset

        self.grid_bottom = self.screen_height - offset
        self.grid_right = self.screen_width - offset

        self.surface = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.font = pygame.font.Font(None, 16)

        self._draw_names = True
        self._draw_reach = False
        self._draw_path = True
        self._draw_threaten = False
        self.char_names = {}
        self._text_layer = []

    # Convert grid coordinates to screen
    def grid_to_screen(self, pt):
        if len(pt) == 2:
            return int(self.grid_left + pt[0] * TILESIZE), int(self.grid_top + pt[1] * TILESIZE)
        else:
            return (int(self.grid_left + pt[0] * TILESIZE),
                    int(self.grid_top + pt[1] * TILESIZE),
                    int(pt[2] * TILESIZE),
                    int(pt[3] * TILESIZE))

    # Convert screen coordinate to grid
    def screen_to_grid(self, pt):
        if len(pt) == 2:
            return ((pt[0] - self.grid_left) / TILESIZE,
                    (pt[1]-self.grid_top) / TILESIZE)
        elif len(pt) == 4:
            return ((pt[0] - self.grid_left) / TILESIZE,
                    (pt[1] - self.grid_top) / TILESIZE,
                    math.ceil(pt[2]/TILESIZE),
                    math.ceil(pt[3]/TILESIZE))

    def clear(self):
        self.surface.fill(BLACK)

    # Draw grid
    def draw_grid(self, grid):

        # Draw vertical lines
        for col in range(grid.get_width()+1):
            pygame.draw.line(self.surface, GREY0, (self.grid_left + col * TILESIZE, self.grid_top),
                             (self.grid_left + col * TILESIZE, self.grid_bottom))

        # Draw horizontal lines
        for row in range(grid.get_height()+1):
            pygame.draw.line(self.surface, GREY0, (self.grid_left, self.grid_top + row * TILESIZE),
                             (self.grid_right, self.grid_top + row * TILESIZE))

        # Draw tiles
        '''
        for tile in grid.get_tiles():
            color = WHITE
            if tile.terrain == TERRAIN_FREE:
                continue
            if tile.terrain == TERRAIN_GRASS:
                color = GREEN0
            coord = tile.get_coord()
            offset = 0.2
            dst_rect = (coord.x + offset, coord.y + offset, 1.0 - 2*offset, 1.0 - 2*offset)
            pygame.draw.rect(self.surface, color, self.grid_to_screen(dst_rect))
        '''

    def draw_tiles(self, grid):
        self._tiler.update(grid)
        # Draw tiles
        for tile in grid.get_tiles():
            dst_rect = self.grid_to_screen((tile.x, tile.y-0.5, 1.0, 1.0))
            self._tiler.draw_tile(self.surface, dst_rect, tile.x, tile.y)

    # Draw tiled path
    def draw_path(self, path, color=GREEN):
        prev = None
        for tile in path.get_path():
            if prev is not None:
                coord_prev = self.grid_to_screen((prev.x+0.5, prev.y+0.5))
                coord_cur = self.grid_to_screen((tile.x+0.5, tile.y+0.5))
                pygame.draw.line(self.surface, color, coord_prev, coord_cur)
            prev = tile

    # Return font texture
    def get_text(self, text):
        text_surface = None
        if text in self.char_names:
            text_surface = self.char_names[text]
        else:
            text_surface = self.font.render(text, 1, WHITE)
            self.char_names[text] = text_surface
        return text_surface

    def draw_combatant(self, u: Combatant):

        color = BLUE

        size = u.get_size()
        coord = self.grid_to_screen((u.visual_X + size * 0.5, u.visual_Y + size * 0.5))
        # pygame.draw.rect(self.surface, coord, row * TILESIZE, TILESIZE, TILESIZE)
        #pygame.draw.circle(self.surface, RED, coord, int(size*TILESIZE * 0.5))
        pygame.draw.circle(self.surface, color, coord, math.ceil(size*TILESIZE * 0.5))
        rect = self.grid_to_screen((u.visual_X, u.visual_Y, size, size))

        arc_width = 2
        percent = u.health / u.health_max
        if percent < 0:
            percent = 0
        angle = 2*math.pi*percent
        if percent > 0:
            pygame.draw.arc(self.surface, GREEN0, rect, 0, angle, arc_width)
        if percent < 1.0:
            pygame.draw.arc(self.surface, RED, rect, angle, math.pi*2, arc_width)
        # pygame.draw.

        if self._draw_path and u.path is not None:
            self.draw_path(u.path)

        if self._draw_threaten:
            for tile in u.threatened_tiles:
                coord_cur = self.grid_to_screen((tile.x + 0.5, tile.y + 0.5))
                pygame.draw.line(self.surface, RED, coord, coord_cur)

        text_surface = self.get_text(u.name)
        if text_surface:
            text_width = text_surface.get_width()
            text_coord = (coord[0] - text_width / 2, coord[1] - size*TILESIZE*0.5-TILESIZE*0.3)
            self._text_layer.append(Renderer.Sprite(text_coord, text_surface))
            #self.surface.blit(text_surface, text_coord)

    def draw_combatants(self, combatants):
        for u in combatants:
            self.draw_combatant(u)

    def draw_battle(self, battle):
        self._text_layer = []
        self.draw_tiles(battle.grid)
        self.draw_grid(battle.grid)
        self.draw_combatants(battle.combatants)
        for text in self._text_layer:
            self.surface.blit(text.surface, text.coord)