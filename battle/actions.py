#!/usr/local/env python3
from .battle import *


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


class WaitAction(BattleAction):
    """
    Implements an action that does nothing
    """

    def __init__(self, combatant):
        super(WaitAction, self).__init__(combatant)
        pass

    def execute(self, battle, state):
        pass

    def text(self):
        return "waits"


class EndTurnAction(BattleAction):
    """
    Implements the action that ends the turn
    """
    def __init__(self):
        super(EndTurnAction, self).__init__()

    def execute(self, battle: Battle, state: TurnState):
        pass

    def text(self):
        return "ends its turn"


class FullRoundAttackAction(BattleAction):
    """
    Implements full round attack
    """
    def __init__(self, combatant, target):
        super(FullRoundAttackAction, self).__init__(combatant)
        self._target = target

    def execute(self, battle: Battle, state: TurnState):
        attack_roll = dice.d20.roll() + self._combatant.get_attack()
        if attack_roll > self._target.get_AC(self._target):
            damage = dice.d6.roll() + self._combatant.strength_modifier()
            battle.deal_damage(self._combatant, self._target, damage)
        else:
            print("%s misses %s with roll=%d"% (self._combatant.get_name(), str(self._target), attack_roll))
        # Mark that we have used an action
        state.use_full_round()

    def text(self):
        return " makes full round attack at %s" % self._target

    # Get duration of the action
    def duration(self):
        return DURATION_FULLROUND


class StandardAttackAction(BattleAction):
    """
    Implements full round attack
    """
    def __init__(self, combatant, target: Combatant):
        super(StandardAttackAction, self).__init__(combatant)
        self._target = target

    def execute(self, battle: Battle, state: TurnState):
        attack_roll = dice.d20.roll() + self._combatant.get_attack()
        if attack_roll > self._target.get_AC():
            damage = dice.d6.roll() + self._combatant.strength_modifier()
            battle.deal_damage(self._combatant, self._target, damage)
        # Mark that we have used an action
        state.use_standard()

    def text(self):
        return " attacks %s" % self._target


class ChargeAttack(BattleAction):
    """
    Implements charge attack
    """
    def __init__(self, combatant, target):
        super(ChargeAttack, self).__init__(combatant)
        self._target = target

    def duration(self):
        return DURATION_FULLROUND


class MoveAction(BattleAction):
    """
    Implements an action that moves a combatant

    :type _path: Path
    :type _combatant: Combatant

    #TODO: each movement should cause attack of opportunity
    """
    def __init__(self, combatant, path):
        super(MoveAction, self).__init__(combatant)
        """
        :param Combatant combatant: The combatant to move
        :param Path path: The path the combatant takes to move
        """

        self._path = path
        self._last_target = None

    def duration(self):
        return DURATION_MOVE

    def execute(self, battle: Battle, state: TurnState):
        # We should iterate all the tiles
        start = self._path.first()
        end = self._path.last()
        tile_src = battle.tile_for_combatant(self._combatant)
        tile_next = None

        #[0,1,2,3,4,5,6]
        #[0,0,0,T,T,0,0]
        # Moves: 0->3, 3->4, 4->6
        for tile in self._path.get_path():
            if tile == tile_src:
                continue
            tile_next = tile
            if tile.is_threatened(self._combatant):
                battle.move_combatant(self._combatant, tile_next)
                tile_next = None

            state.moves_left -= 5
            if state.moves_left == 0:
                break
        # One last step
        if tile_next is not None:
            battle.move_combatant(self._combatant, tile_next)

        state.use_move()

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
