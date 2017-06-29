import pygame
import math
from battle.combatant import Combatant

# Pixel size for a tile
TILESIZE=16

# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)


class Renderer:
    def __init__(self, grid, offset = 0):
        self.grid_top = offset
        self.grid_left = offset

        self.screen_width = grid.get_width() * TILESIZE + 2 * offset
        self.screen_height = grid.get_height() * TILESIZE + 2 * offset

        self.grid_bottom = self.screen_height - offset
        self.grid_right = self.screen_width - offset

        self.surface = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.font = pygame.font.Font(None, 24)

        self._draw_names = True
        self._draw_reach = True
        self._draw_path = True
        self._draw_threaten = True

        self.char_names = {}

    # Convert grid coordinates to screen
    def grid_to_screen(self, pt):
        if len(pt) == 2:
            return (int(self.grid_left + pt[0] * TILESIZE), int(self.grid_top + pt[1] * TILESIZE))
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
            pygame.draw.line(self.surface, WHITE, (self.grid_left + col * TILESIZE, self.grid_top), (self.grid_left + col * TILESIZE, self.grid_bottom))

        # Draw horizontal lines
        for row in range(grid.get_height()+1):
            pygame.draw.line(self.surface, WHITE, (self.grid_left, self.grid_top + row * TILESIZE), (self.grid_right, self.grid_top + row * TILESIZE))

        # Draw tiles
        for tile in grid.get_tiles():
            color = WHITE
            if tile._terrain != 0:
                rect = (*tile.coords(), 1, 1)
                pygame.draw.rect(self.surface, color, self.grid_to_screen(rect))


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
        coord = self.grid_to_screen((u.X + 0.5, u.Y + 0.5))
        color = BLUE

        # pygame.draw.rect(self.surface, coord, row * TILESIZE, TILESIZE, TILESIZE)
        pygame.draw.circle(self.surface, color, coord, int(TILESIZE / 2))
        # pygame.draw.

        text_surface = self.get_text(u.get_name())
        if text_surface:
            text_width = text_surface.get_width()
            text_coord = (coord[0]-text_width/2, coord[1]-TILESIZE)
            self.surface.blit(text_surface, text_coord)

        if self._draw_path and u.path is not None:
            self.draw_path(u.path)

        for tile in u._threatened_tiles:
            coord_cur = self.grid_to_screen((tile.x + 0.5, tile.y + 0.5))
            pygame.draw.line(self.surface, RED, coord, coord_cur)

    def draw_combatants(self, combatants):
        for u in combatants:
            self.draw_combatant(u)