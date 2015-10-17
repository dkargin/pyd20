import math
from grid import PriorityQueue, Tile
from battle.actions import BattleAction, EndTurnAction, MoveAction


class Battle(object):

    """
    Models a battle

    :type grid: grid.Grid
    :type _combatants: Combatant[]
    """

    def __init__(self, grid):
        """
        Create an instance of a battle.

        :param Grid grid: The grid the battle takes place on
        """
        self.grid = grid
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
        position = self.grid.get_tile(x, y)
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
            print(combatant, "'s turn")
            action = BattleAction()
            while not isinstance(action, EndTurnAction):
                action = combatant.next_action(self)
                if not action.can_execute(combatant):
                    continue
                combatant.remove_action_points(action.action_point_cost())
                action.execute()

    def tile(self, *args, **kwargs):
        """
        Returns the tile for a combatant or a position.

        possible arguments are:
        :param Combatant combatant: The combatant
        :param int x: Position x
        :param int y: Position y

        :rtype: Tile
        """
        combatant = kwargs.get("combatant", None)
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        if combatant is not None:
            return self.__tile_for_combatant(combatant)
        if x is not None and y is not None:
            return self.__tile_for_position(x, y)

    def __tile_for_combatant(self, combatant):
        for tile in self.grid.get_tiles():
            if tile.has_occupation(combatant):
                return tile
        return None

    def __tile_for_position(self, x, y):
        return self.grid.get_tile(x, y)


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
        self._current_initiative = 0

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
