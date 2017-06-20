import math
import logging
from battle.actions import *

class Brain(object):
    def __init__(self):
        self.slave = None
        # Attack target
        self.target = None
        # Path to follow
        self.path = None

    # To be overriden
    def make_turn(self, battle, state):
        pass


# Object is controlled by keyboard input
class ManualBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        pass

# Brain for simple movement and attacking
class MoveAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        self.logger = logging.getLogger("brain")

    def make_turn(self, battle, state: TurnState):
        # 1. If no enemy - find it
        if self.target is None:
            print("Has no target. Finding")
            self.target = battle.find_enemy(self.slave)

        if self.target is None:
            return []

        # 2. If enemy is in range - full round attack
        if battle.is_adjacent(self.slave, self.target):
            self.logger.debug("target is near, can attack")
            if state.fullround_actions > 0:
                yield FullRoundAttackAction(self.slave, self.target)
            else:
                yield StandardAttackAction(self.slave, self.target)
        else:
            self.logger.debug("farget %s is away. Finding path" % self.target.get_name())
            start = battle.tile_for_combatant(self.slave)
            end = battle.tile_for_combatant(self.target)
            path = battle.pathfinder.path_between_tiles(start, end)
            self.logger.debug("found path of %d feet length" % path.length())
            yield MoveAction(self.slave, path)

        '''
        2. If enemy is near 5ft - move and full round
        If enemy is far - move to it
        3. If enemy is near for charge - do it
        4.
        :param battlefield:
        :return:
        '''
        return

