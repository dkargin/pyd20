#!/usr/local/env python3
from .battle import *

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
    def __init__(self, combatant: Combatant):
        self._combatant = combatant

    # Get duration of the action
    def duration(self):
        return DURATION_STANDARD

    def can_execute(self, combatant):
        return False

    def execute(self, battle: Battle, state: TurnState):
        pass

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

    def execute(self, battle: Battle, state: TurnState):
        pass

    def text(self):
        return "ends its turn"


class EndTurnAction(BattleAction):
    """
    An empty animation action. Returned when there are no other actions available
    """

    def __init__(self, combatant):
        super(EndTurnAction, self).__init__(combatant)

    def execute(self, battle: Battle, state: TurnState):
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

    def execute(self, battle: Battle, state: TurnState):
        desc = self._desc
        target = desc.get_target()
        attack_roll = desc.roll_attack()
        crit_confirm = desc.roll_attack()

        # TODO: run events for on_strike_begin(desc, target)
        AC = target.get_touch_ac(target) if desc.touch else target.get_AC(target)

        if desc.is_critical(attack_roll):
            # TODO: run events for critical hit
            pass

        if attack_roll >= AC:
            damage = desc.roll_damage()
            print("%s hits %s with roll %d vs AC=%d" % (self._combatant.get_name(), target.get_name(), attack_roll, AC))
            battle.deal_damage(self._combatant, target, damage)
        else:
            print ("%s misses %s with roll %d vs AC=%d" % (self._combatant.get_name(), target.get_name(), attack_roll, AC))
            # TODO: run events for on_strike_finish()

    def text(self):
        return " attacks %s" % self._target

    def is_attack_action(self):
        return True

    def is_move_action(self):
        return False


class MoveAction(BattleAction):
    """
    Implements an action that moves a combatant

    :type _start: Tile starting tile
    :type _finish: Tile finish tile

    #TODO: each movement should cause attack of opportunity
    """
    def __init__(self, combatant, tiles, provoke = False):
        super(MoveAction, self).__init__(combatant)
        self._finish = tiles[len(tiles)-1]
        self._provoke = provoke

    def duration(self):
        return DURATION_MOVE

    def execute(self, battle: Battle, state: TurnState):
        combatant = self._combatant
        start = battle.tile_for_combatant(combatant)
        if start == self._finish:
            return

        print("moving %s from %s to %s" % (str(combatant), str(start), str(self._finish)))
        # AoO can interupt movement
        # 5ft step still can provoke
        # Not moving still can provoke
        success = True
        AoOs = battle.opportunity_provoke(combatant, self)

        for attack in AoOs:
            # TODO: roll AoO and check if it really interrupts
            pass

        if not success:
            return False

        battle.grid.unregister_entity(combatant)

        combatant.x = self._finish.x
        combatant.y = self._finish.y

        battle.grid.register_entity(combatant)
        return True

    def can_execute(self, combatant, state: TurnState):
        return state.move_actions > 0 and state.moves_left > 0

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
        super(UseSkillAction, self).__init__()
        self._character = character
        self._target = target
        self._skill_name = skill_name

    def execute(self, battle: Battle, state: TurnState):
        self._character.use_skill(self._skill_name)
