import logging
import cProfile, pstats
import pygame

from battle_utils import *
from render.render import Renderer
import sim.battle as battle
import sim.events as events
from sim.dice import d20

logger = logging.getLogger(__name__)

"""
char = Character("dummy")


def remove_min(stats):
    min_stat = stats[0]
    for i in stats:
        if i < min_stat:
            min_stat = i
    stats.remove(min_stat)
    return sorted(stats)

generated = 0
while generated < 3:
    stats = remove_min([d20.roll() for i in range(0, 7)])
    char.set_stats(*tuple(stats))
    sum_mod = 0

    sum_mod += char.strength_modifier()
    sum_mod += char.dexterity_modifier()
    sum_mod += char.constitution_modifier()
    sum_mod += char.intellect_modifier()
    sum_mod += char.wisdom_modifier()
    sum_mod += char.charisma_modifier()

    if sum_mod <= 1:
        print("%s - rejected, sum_mod=%d" % (stats, sum_mod))
    else:
        print("%s - sum_mod=%d" % (stats, sum_mod))
        generated+=1
"""

center_x = 15
center_y = 15

battle = battle.Battle(30, 30)

draw_block(battle.grid, TERRAIN_WALL, 3, 3, 2, 8)

char1 = Character("Bob", brain=brain.StandAttackBrain(), model='type3')
char1.set_stats(18, 18, 16, 10, 10, 10)
char1.wear_item(dnd.armor.chain_shirt, ITEM_SLOT_ARMOR)
char1.wear_item(dnd.weapon.bastard_sword, ITEM_SLOT_MAIN)
char1.wear_item(dnd.weapon.longsword, ITEM_SLOT_OFFHAND)
char1.add_class_level(classes.Fighter, 8)
char1.add_feat(dnd.feats.TwoWeaponFighting())
char1.add_feat(dnd.feats.ImprovedTwoWeaponFighting())
char1.add_feat(dnd.feats.OversizedTwoWeaponFighting())
char1.add_feat(dnd.feats.PowerCritical(dnd.weapon.glaive))

'''
char1 = Character("Bob", csize=SIZE_LARGE, brain=brain.StandAttackBrain(), model='type3')
char1.set_stats(18, 16, 16, 10, 10, 10)
char1.wear_item(dnd.armor.breastplate, ITEM_SLOT_ARMOR)
char1.wear_item(dnd.weapon.glaive, ITEM_SLOT_MAIN)
char1.add_class_level(classes.Fighter, 6)
char1.add_feat(dnd.feats.CombatReflexes())
char1.add_feat(dnd.feats.DeftOpportunist())
char1.add_feat(dnd.feats.WeaponFocus(dnd.weapon.glaive))
char1.add_feat(dnd.feats.PowerCritical(dnd.weapon.glaive))
'''


char2 = make_shield_fighter('Roy1', model='type2')
char3 = make_archer('Bowy')
char4 = make_monk('Monky')

char_test = make_angry_guisarme('Goof', model='type3')


# tile = grid.get_free_tile()
battle.add_combatant(char1, center_x-2, center_y+1, faction="team red")
battle.add_combatant(char2, center_x+10, center_y+1, faction="team blue")

#battle.add_combatant(char3, center_x+10, center_y-5, faction="team blue")
#battle.add_combatant(char4, center_x + 10, center_y-4, faction="team blue")
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
                animation.on_stop(time)
                animation = None


        if animation is None and ((wait_turn and make_turn) or not wait_turn):
            battle_event = next(turn_generator)
            wait_turn = False
            if isinstance(battle_event, events.RoundEnd):
                # Make character prone, to test 'StandUp'
                # char1.add_status_flag(STATUS_PRONE)
                print("Press key for the next turn")
                wait_turn = True
            elif isinstance(battle_event, events.AnimationEvent):
                logger.info("Got animation: %s" % str(animation))
                animation = battle_event.animation
                animation.on_start(get_time())

        renderer.clear()
        renderer.draw_battle(battle)
        pygame.display.flip()

    print("Done")
    pygame.quit()

if __name__ == '__main__':
    profile = False
    if profile:
        cProfile.run('main()', 'restats')
        print("Preparing profiler statistics")
        stats = pstats.Stats('restats')
        stats.strip_dirs().sort_stats(1).print_stats()
    else:
        main()
