import logging
import cProfile, pstats
import pygame

from battle_utils import *
from render.render import Renderer
import battle.battle as battle
import battle.events as events

logger = logging.getLogger(__name__)


center_x = 15
center_y = 15

battle = battle.Battle(30, 30)

draw_cross(battle.grid, center_x, center_y, 5)
draw_cross(battle.grid, center_x+1, center_y, 5)
draw_block(battle.grid, TERRAIN_WALL, 3, 3, 2, 8)


char1 = Character("Bob", csize=SIZE_LARGE, brain=brain.StandAttackBrain(), model='type2')
char1.set_stats(18, 16, 16, 10, 10, 10)
char1.wear_item(dnd.armor.breastplate, ITEM_SLOT_ARMOR)
char1.wear_item(dnd.weapon.glaive, ITEM_SLOT_MAIN)
char1.add_class_level(classes.Fighter, 6)
char1.add_feat(dnd.feats.CombatReflexes())
char1.add_feat(dnd.feats.DeftOpportunist())
char1.add_feat(dnd.feats.WeaponFocus(dnd.weapon.glaive))
char1.add_feat(dnd.feats.PowerCritical(dnd.weapon.glaive))


char2 = make_shield_fighter('Roy1')
char2.model = 'type2'
#char3 = make_twf_fighter('Roy2')
char4 = make_monk('Monky')


#battle.add_combatant(char1, *grid.get_free_tile(), faction="team red")
#battle.add_combatant(char2, *grid.get_free_tile(), faction="team blue")
battle.add_combatant(char1, center_x-2, center_y+1, faction="team red")

battle.add_combatant(char2, center_x + 10, center_y, faction="team blue")
#battle.add_combatant(char3, center_x + 15, center_y-5, faction="team blue")
battle.add_combatant(char4, center_x + 10, center_y-4, faction="team blue")
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


# Get current time, in seconds
def get_time():
    return pygame.time.get_ticks()*0.001


def main():
    battle.print_characters()
    renderer = Renderer(battle, 20)

    pygame.display.set_caption("Battlescape")

    shouldExit = False
    animation = None

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
            '''
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                move_dir = ( 0,-1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                move_dir = ( 0, 1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                move_dir = ( 1, 0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                move_dir = (-1, 0)
            '''

        if animation is not None:
            time = get_time()
            animation.update(time)
            if animation.is_complete(time):
                logging.info("%s is complete" % animation)
                animation = None

        if animation is None and ((wait_turn and make_turn) or not wait_turn):
            battle_event = next(turn_generator)
            wait_turn = False
            if isinstance(battle_event, events.RoundEnd):
                print("Press key for the next turn")
                wait_turn = True
            elif isinstance(battle_event, events.AnimationEvent):
                logger.info("Got animation: %s" % str(animation))
                animation = battle_event.animation
                animation.start(get_time())

        renderer.clear()
        renderer.draw_battle(battle)
        pygame.display.flip()

    print("Done")
    pygame.quit()

if __name__ == '__main__':
    cProfile.run('main()', 'restats')
    print("Preparing profiler statistics")
    stats = pstats.Stats('restats')
    stats.strip_dirs().sort_stats(1).print_stats()
