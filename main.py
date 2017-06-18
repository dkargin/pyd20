import pygame, sys
from battle.battle import Battle
from character import Character
from grid import Grid, PathFinder
import brain

from pygame.locals import *
from render import Renderer

pygame.init()


grid = Grid(40, 40)
battle = Battle(grid)

char1 = Character("Char1")
char2 = Character("Char2")

char1.set_brain(brain.MoveAttackBrain())
char2.set_brain(brain.MoveAttackBrain())

battle.add_combatant(char1, *grid.get_free_tile())
battle.add_combatant(char2, *grid.get_free_tile())

start = grid.get_tile(*char1.coords())
end = grid.get_tile(*char2.coords())

#pathfinder = PathFinder(grid)
#path = pathfinder.path_between_tiles(start, end)

#assert path is not None
#assert path.length() > 0

renderer = Renderer(grid, 20)

pygame.display.set_caption("Battlescape")

shouldExit = False
while not shouldExit:
    make_turn = False
    move_dir = None
    # Collect events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shouldExit = True
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            make_turn = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            move_dir = ( 0,-1)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            move_dir = ( 0, 1)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            move_dir = ( 1, 0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            move_dir = (-1, 0)
    # Process events
    if make_turn:
        battle.next_round()

    renderer.draw_grid(grid)
    #renderer.draw_path(path)
    renderer.draw_combatants(battle._combatants)
    pygame.display.update()


print("Done")
pygame.quit()