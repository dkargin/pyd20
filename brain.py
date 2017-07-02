import math
import logging
from battle.actions import *
from battle.combatant import *

class Brain(object):
    """
    :type slave: Combatant | None
    :type target: Combatant | None
    """
    def __init__(self):
        self.slave = None
        # Attack target
        self.target = None
        # Path to follow
        self.path = None

    # To be overriden
    def make_turn(self, battle):
        pass

    def respond_provocation(self, battle, target : Combatant, action=None):
        state = self.get_turn_state()
        if self.slave.opportunities_left() > 0 and state.attack_AoO is not None:
            print("%s uses opportinity to attack %s" % (self.slave.get_name(), target.get_name()))
            desc = state.attack_AoO.copy()
            desc.update_target(target)
            self.slave.use_opportunity(desc)
            yield from battle.do_action_strike(self.slave, desc)

    def get_turn_state(self) -> TurnState:
        return self.slave.get_turn_state()


# Brain for simple movement and attacking
class MoveAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        self.logger = logging.getLogger("brain")

    def make_turn(self, battle):
        state = self.get_turn_state()
        # Trying iteratively use all turn actions
        # 1. If no enemy - find it
        if self.target is None:
            self.target = battle.find_enemy(self.slave)
            if self.target is not None:
                print("%s found enemy: %s" %(self.slave.get_name(), str(self.target)))

        if self.target is None:
            print("%s has no targets" % self.slave.get_name())
            #yield WaitAction(self.slave)
            return

        # 2. If enemy is in range - full round attack
        if self.slave.is_adjacent(self.target):
            self.logger.debug("target is near, can attack")
            while state.can_attack():
                if self.target.is_consciousness():
                    # Mark that we have used an action
                    desc = state.use_attack()
                    desc.update_target(self.target)
                    # TODO: update attack data according to selected target or custom attack
                    yield from battle.make_action_strike(self.slave, state, self.target, desc)
                else:
                    self.target = None
                    break
        elif state.can_move():
            self.logger.debug("farget %s is away. Finding path" % self.target.get_name())
            path = battle.path_to_melee_range(self.slave, self.target, self.slave.total_reach())
            self.logger.debug("found path of %d feet length" % path.length())
            yield from battle.make_action_move_tiles(self.slave, state, path)


# Brain that attacks only if enemy is adjacent
class StandAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        self.logger = logging.getLogger("brain")

    def make_turn(self, battle):
        state = self.get_turn_state()
        # Trying iteratively use all turn actions
        # 1. If no enemy - find it
        if self.target is None:
            self.target = battle.find_enemy(self.slave)
            if self.target is not None:
                print("%s found enemy: %s" %(self.slave.get_name(), str(self.target)))

        if self.target is None:
            print("%s has no targets" % self.slave.get_name())
            #yield WaitAction(self.slave)
            return

        # 2. If enemy is in range - full round attack
        if not self.slave.is_adjacent(self.target):
            self.logger.debug("target is far, can not attack")
            return

        self.logger.debug("target is near, can attack")
        while state.can_attack():
            if self.target.is_consciousness():
                # Mark that we have used an action
                desc = state.use_attack()
                desc.update_target(self.target)
                # TODO: update attack data according to selected target or custom attack
                yield from battle.make_action_strike(self.slave, state, self.target, desc)
            else:
                self.target = None
                break


# Object is controlled by keyboard input
class ManualBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        pass
