#!/usr/local/env python3
from .battle import *
from .core import *
import animation
import battle.events as events

ACTION_RESULT_SUCCESS = 0
ACTION_RESULT_FAILED = 1

"""
BattleAction - elementary action. It is executed separately and cannot interrupted.
This action cannot be 'half done'. It is either succeded, or failed

Some action can be groupped in action sequence. Action sequence can be interrupted. AI shoud decide
in that case what to do next. TurnState will contain information about current 'time' limitations

Elementary actions:
 - Move between unthreatened tiles
 - Attack
 - Cast a spell
 - Jump. Part of a move
 - Tumble. Part of move?
 - Stand up
 - Use an item

Sequences:
 - Fullround attack: action sequence {Attack1, Attack2, Attack3}
    - Some attacks can provide additional 'free' attacks
 - Charge: {Move, Attack}
 - ChargePounce: {Move, Attack1, Attack2, ...}
 - SpringAttack/MoveAndShoot: {Move, Attack, Move}
 - BoundingAssault: {Move, Attack, Move}



Update combatants
           -> brain.gen_actions
    action <- Action1
                        -> execute
                            <- action2
    action <- Action2
    acrion <- Action3...

"""


class BattleAction(object):
    """
    Models an action in a battle. This includes all actions that can
    possibly taken during a battle including, but not limited to:
    Moving, Attacking and using an Ability, Skill or Trait.
    """
    def __init__(self, combatant: Combatant, **kwargs):
        self._combatant = combatant
        self._duration = kwargs.get('duration', DURATION_STANDARD)

    # Get duration of the action
    @property
    def duration(self):
        return self._duration

    def can_execute(self, combatant):
        return False

    def execute(self, battle: Battle, state: TurnState):
        yield

    def _get_turn_state(self):
        return self._combatant.get_turn_state()

    def text(self):
        return "generic action"

    # Returns action text for display
    def action_text(self):
        return "%s executes %s" % (self._combatant.get_name(), self.text())

    # If action is 'move' action
    def is_move_action(self):
        return False

    # If action is 'attack' action
    def is_attack_action(self):
        return False


class EmptyAction(BattleAction):
    """
    An empty animation action. Returned when there are no other actions available
    """
    def __init__(self):
        super(EmptyAction, self).__init__()

    def execute(self, battle: Battle):
        yield

    def text(self):
        return "ends its turn"


class EndTurnAction(BattleAction):
    """
    An empty animation action. Returned when there are no other actions available
    """

    def __init__(self, combatant):
        super(EndTurnAction, self).__init__(combatant)

    def execute(self, battle: Battle):
        pass

    def text(self):
        return "ends its turn"


# Single attack
class AttackAction(BattleAction):
    """
    Implements animation for a single attack
    """
    def __init__(self, combatant, attack_desc: Combatant):
        super(AttackAction, self).__init__(combatant)
        self._desc = attack_desc

    def execute(self, battle: Battle):
        desc = self._desc
        yield from self._combatant.do_action_strike(desc)

    def text(self):
        return " attacks %s" % self._target

    def is_attack_action(self):
        return True

    def is_move_action(self):
        return False


class TripAttackAction(BattleAction):
    def __init__(self, combatant, attack_desc: Combatant):
        super(AttackAction, self).__init__(combatant)
        self._desc = attack_desc

    def execute(self, battle: Battle):
        desc = self._desc
        yield from self._combatant.do_action_trip_attack(desc)

    def text(self):
        return " attacks %s" % self._target

    def is_attack_action(self):
        return True

    def is_move_action(self):
        return False

# Stand up from prone position
class StandUpAction(BattleAction):
    """
    Implements animation for a single attack
    """
    def __init__(self, combatant):
        super(StandUpAction, self).__init__(combatant)
        self._provoke = True

    def execute(self, battle: Battle):
        combatant = self._combatant
        combatant.remove_status_flag(STATUS_PRONE)
        success = True
        if self._provoke:
            enemies = battle.get_threatening_enemies(combatant, self)
            for enemy in enemies:
                yield from enemy.respond_provocation(battle, self._combatant, self)
                # TODO: roll AoO and check if it really interrupts

        if not success:
            return False

    def text(self):
        return " attacks %s" % self._target

    def is_attack_action(self):
        return False

    def is_move_action(self):
        return True


class MoveAction(BattleAction):
    """
    Implements an action that moves a combatant

    :type _start: Tile starting tile
    :type _finish: Tile finish tile

    #TODO: each movement should cause attack of opportunity
    """
    def __init__(self, combatant, tiles, provoke = True, **kwargs):
        super(MoveAction, self).__init__(combatant)
        self._finish = tiles[len(tiles)-1][0]
        self._path = tiles
        self._provoke = provoke

    def cost(self):
        result = 0
        for tile, cost in self._path:
            result += cost
        return result

    @property
    def regular_path(self):
        return [tile for tile, cost in self._path]

    def duration(self):
        return DURATION_MOVE

    def execute(self, battle: Battle):
        combatant = self._combatant
        state = self._get_turn_state()

        print("moving %s from %s to %s, moves=%d, tiles=%d" % (str(combatant), str(combatant.get_coord()), str(self._finish), self.cost(), len(self._path)))
        # AoO can interupt movement
        # 5ft step still can provoke
        # Not moving still can provoke
        success = True
        if self._provoke:
            enemies = battle.get_threatening_enemies(combatant, self)
            for enemy in enemies:
                yield from enemy.respond_provocation(battle, self._combatant, self)
                # TODO: roll AoO and check if it really interrupts

        if not success:
            return False

        battle.grid.unregister_entity(combatant)

        combatant.x = self._finish.x
        combatant.y = self._finish.y

        battle.grid.register_entity(combatant)
        yield events.AnimationEvent(animation.MovePath(combatant, self.regular_path))
        combatant.fix_visual()

    def text(self):
        return "moves to %s" % self._last_target


class UseSkillAction(BattleAction):
    """
    Implements an action that uses a skill

    :type _character: Character
    :type _target: Combatant
    :type _skill_name: string
    """

    def __init__(self, character, target, skill_name):
        """
        :param Character character: The character that executes the skill
        :param Combatant target: The target to use the skill on
        """
        super(UseSkillAction, self).__init__(character)
        self._target = target
        self._skill_name = skill_name

    def execute(self, battle: Battle):
        self._combatant.use_skill(self._skill_name)
