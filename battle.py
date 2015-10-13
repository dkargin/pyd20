import character


class Battle:

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
        self._combatants = []
        pass

    def add_combatant(self, entity, x, y):
        combatant = Combatant(entity)
        position = self._grid.get_tile(x, y)
        position.add_occupation(combatant)
        self._combatants.append(combatant)

    def next_round(self):
        for combatant in self._combatants:
            combatant.reset_round()


class Combatant:

    """
    :type _is_flat_footed: bool
    :type _entity: character.Character
    :type _action_points: int
    """

    def __init__(self, entity):
        """
        :param character.Character entity:
        """
        self._entity = entity
        self._is_flat_footed = False
        self._action_points = 3

    def reset_round(self):
        self._is_flat_footed = False
        self._action_points = 3

    def initiative(self):
        return self._entity.initiative()