import character
import core

class Battle:

    def __init__(self):
        pass


class Combatant:

    """
    :type _character: character.Character
    """

    def __init__(self, character):
        self._is_flat_footed = False
        self._character = character

    def initiative(self):
        return self._character.initiative()