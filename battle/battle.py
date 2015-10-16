from grid import PriorityQueue
from actions import *


class Battle(object):

    """
    Models a battle

    :type _grid: grid.Grid
    :type _combatants: Combatant[]
    """

    def __init__(self, grid):
        """
        Create an instance of a battle.

        :param Grid grid: The grid the battle takes place on
        """
        self._grid = grid
        self._combatants = PriorityQueue()

    def add_combatant(self, combatant, x, y):
        """
        Adds a combatant to the battle. This is typically a Character or a Monster.
        If the grid has no tile at the specified position, the combatant will not
        be added to the battle

        :param Combatant combatant: The combatant
        :param int x: The x position on the grid
        :param int y: The y position on the grid
        """
        position = self._grid.get_tile(x, y)
        if position is None:
            return
        position.add_occupation(combatant)
        self._combatants.append(combatant, combatant.current_initiative())

    def next_round(self):
        """
        Ends the current round and starts a new round, resulting in new initiative rolls
        and reset action points.
        """
        for combatant in self._combatants:
            combatant.reset_round()
            self._combatants.update_priority(combatant, combatant.current_initiative())
        for combatant in self._combatants:
            action = BattleAction()
            while not isinstance(action, EndTurnAction):
                action = combatant.next_action(self)
                if not action.can_execute(combatant):
                    continue
                combatant.remove_action_points(action.action_point_cost())
                action.execute()


class Combatant(object):

    """
    :type _is_flat_footed: bool
    :type _action_points: int
    :type _current_initiative: int
    """

    def __init__(self):
        """
        :param Character entity:
        """
        self._is_flat_footed = False
        self._action_points = 3
        self._current_initiative = self.initiative()

    def reset_round(self):
        """
        Resets the round for this combatant
        """
        self._is_flat_footed = False
        self._action_points = 3
        self._current_initiative = self.initiative()

    def current_initiative(self):
        """
        Returns the last rolled initiative
        :rtype: int
        """
        return self._current_initiative

    def initiative(self):
        """
        Should be implemented in subclasses. This method should return
        the initiative value of the combatant

        :rtype: int
        """
        pass

    def next_action(self, battle):
        """
        Should be implemented in subclasses. This method should return
        the next action until no action points are left. If no points
        are left, then an EndTurnAction should be returned.

        :param Battle battle: A reference to the battle taking place
        :rtype: BattleAction
        """
        return EndTurnAction()

    def current_action_points(self):
        """
        Returns the current action points.

        :rtype: int
        """
        return self._action_points

    def remove_action_points(self, amount):
        """
        Removes a specific amount of action points.
        """
        self._action_points -= amount


class BattleAction(object):
    """
    Models an action in a battle. This includes all actions that can
    possibly taken during a battle including, but not limited to:
    Moving, Attacking and using an Ability, Skill or Trait.
    """

    def __init__(self):
        pass

    def action_point_cost(self):
        """
        Should be implemented in subclasses. This method should
        return the amount of action points this action costs to
        execute.
        :rtype: int
        """
        return 0

    def can_execute(self, combatant):
        """
        Checks whether a combatant can execute an anction or not
        :param Combatant combatant: The combatant
        :rtype: bool
        """
        return combatant.current_action_points() >= self.action_point_cost()

    def execute(self):
        """
        Should be implemented in subclasses.
        """
        pass
