import pygame, sys
from battle.battle import Battle
from battle.combatant import Combatant
from character import Character
from grid import *
import brain
import classes
import dnd.armor
import dnd.weapon
import core
import dice

from pygame.locals import *
from render import Renderer

pygame.init()

grid = Grid(40, 40)



center_x = 20
center_y = 20

for i in range(-5, 6):
    grid.set_terrain(center_x, center_y + i, TERRAIN_WALL)
    grid.set_terrain(center_x+ i, center_y, TERRAIN_WALL)


battle = Battle(grid)

char1 = Character("Bob", brain=brain.MoveAttackBrain())
char1.set_stats(18, 13, 16, 10, 10, 10)
char1.wear_item(dnd.armor.full_plate, core.ITEM_SLOT_ARMOR)
char1.wear_item(dnd.weapon.glaive, core.ITEM_SLOT_MAIN)
char1.add_class_level(classes.Fighter, 6)

# Create shield fighter
def make_shield_fighter(name, stats=[18, 13, 16, 10, 10, 10]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, core.ITEM_SLOT_ARMOR)
    char.wear_item(dnd.armor.tower_shield, core.ITEM_SLOT_OFFHAND)
    char.wear_item(dnd.weapon.longsword, core.ITEM_SLOT_MAIN)
    char.add_class_level(classes.Fighter, 6)
    return char

# Create dual weapons fighter
def make_twf_fighter(name, stats=[18, 13, 16, 10, 10, 10]):
    char = Character(name, brain=brain.MoveAttackBrain())
    char.set_stats(*stats)
    char.wear_item(dnd.armor.full_plate, core.ITEM_SLOT_ARMOR)
    char.wear_item(dnd.weapon.longsword, core.ITEM_SLOT_MAIN)
    char.wear_item(dnd.weapon.shortsword, core.ITEM_SLOT_OFFHAND)
    char.add_class_level(classes.Fighter, 6)
    char._twf_skill = 1
    #char.add_feat(feats.TWF)
    return char


char2 = make_shield_fighter('Roy')

char3 = make_twf_fighter('Dancey')

print(char1.print_character())
print(char2.print_character())
print(char3.print_character())

battle.add_combatant(char1, *grid.get_free_tile())
battle.add_combatant(char2, *grid.get_free_tile())

#battle.add_combatant(char1, center_x - 5, center_y)
#battle.add_combatant(char2, center_x + 5, center_y)

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

    renderer.clear()
    renderer.draw_grid(grid)
    renderer.draw_combatants(battle._combatants)
    pygame.display.flip()

print("Done")
pygame.quit()
