from grid import PriorityQueue


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
