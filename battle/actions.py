#!/usr/local/env python3
from .battle import *


class WaitAction(BattleAction):
    """
    Implements an action that does nothing
    """

    def __init__(self):
        super(WaitAction, self).__init__()

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
        pass

    def text(self):
        return " makes full round attack at %s" % self._target

    # Get duration of the action
    def duration(self):
        return DURATION_FULLROUND


class StandardAttackAction(BattleAction):
    """
    Implements full round attack
    """
    def __init__(self, combatant, target):
        super(StandardAttackAction, self).__init__(combatant)
        self._target = target

    def execute(self, battle: Battle, state: TurnState):
        pass

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
