import logging

import pygame

from battle_utils import *
from render import Renderer
from battle.battle import Battle

logger = logging.getLogger(__name__)

pygame.init()

center_x = 20
center_y = 20

battle = Battle(40, 40)

#draw_cross(battle.grid, center_x, center_y, 5)

char1 = Character("Bob", size=2, brain=brain.StandAttackBrain())
char1.set_stats(18, 16, 16, 10, 10, 10)
char1.wear_item(dnd.armor.breastplate, ITEM_SLOT_ARMOR)
char1.wear_item(dnd.weapon.glaive, ITEM_SLOT_MAIN)
char1.add_class_level(classes.Fighter, 6)
char1.add_feat(dnd.feats.CombatReflexes())
char1.add_feat(dnd.feats.DeftOpportunist())


char2 = make_shield_fighter('Roy1')
char3 = make_twf_fighter('Roy2')
char4 = make_monk('Monky')

#char5 = make_shield_fighter('Roy4')

#battle.add_combatant(char1, *grid.get_free_tile(), faction="team red")
#battle.add_combatant(char2, *grid.get_free_tile(), faction="team blue")
battle.add_combatant(char1, center_x, center_y, faction="team red")

battle.add_combatant(char2, center_x + 15, center_y, faction="team blue")
battle.add_combatant(char3, center_x + 15, center_y-5, faction="team blue")
battle.add_combatant(char4, center_x + 15, center_y-4, faction="team blue")
"""
battle.add_combatant(char5, center_x + 15, center_y-3, faction="team blue")
"""


# Drawing attack positions by specifying reach range
def draw_attack_positions(grid, combatant, reach0, reach1):
    tiles0 = grid.get_tile_range(combatant.get_center(), combatant.get_size()*0.5+reach0)
    tiles1 = grid.get_tile_range(combatant.get_center(), combatant.get_size()*0.5+reach1)

    for tile in tiles0:
        if tile in tiles1:
            continue
        tile.set_terrain(TERRAIN_GRASS)

battle.print_characters()

renderer = Renderer(battle, 20)

pygame.display.set_caption("Battlescape")

shouldExit = False
animation = None


# Get current time, in seconds
def get_time():
    return pygame.time.get_ticks()*0.001

turn_generator = battle.battle_generator()
wait_turn = True

while not shouldExit:
    make_turn = False
    pygame.time.wait(30)
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

    if animation is not None:
        time = get_time()
        animation.update(time)
        if animation.is_complete(time):
            logging.info("%s is complete" % animation)
            animation = None

    if animation is None and ((wait_turn and make_turn) or not wait_turn):
        animation = next(turn_generator)
        if animation is None:
            print("Press key for the next turn")
        else:
            logger.info("Got animation: %s" % str(animation))

            animation.start(get_time())
        wait_turn = animation is None

    renderer.clear()
    renderer.draw_battle(battle)
    pygame.display.flip()

print("Done")
pygame.quit()
