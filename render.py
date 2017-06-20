import pygame

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

    # Convert grid coordinates to screen
    def grid_to_screen(self, pt):
        return (int(self.grid_left + pt[0]*TILESIZE), int(self.grid_top + pt[1] * TILESIZE))

    # Convert screen coordinate to grid
    def screen_to_grid(self, pt):
        return ((pt[0] - self.grid_left) / TILESIZE, (pt[1]-self.grid_top) / TILESIZE)

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
            col = tile.x
            row = tile.y
            color = WHITE
            if tile._terrain != 0:
                pygame.draw.rect(self.surface, col * TILESIZE, row*TILESIZE, TILESIZE, TILESIZE)

    # Draw tiled path
    def draw_path(self, path, color=GREEN):
        prev = None
        for tile in path.get_path():
            if prev is not None:
                coord_prev = self.grid_to_screen((prev.x+0.5, prev.y+0.5))
                coord_cur = self.grid_to_screen((tile.x+0.5, tile.y+0.5))
                pygame.draw.line(self.surface, color, coord_prev, coord_cur)
            prev = tile

    def draw_combatants(self, combatants):
        for u in combatants:
            coord = self.grid_to_screen((u.X + 0.5, u.Y + 0.5))
            color = BLUE
            pygame.draw.circle(self.surface, color, coord, int(TILESIZE/2))
            #pygame.draw.