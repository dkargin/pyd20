class Item(object):
    """
    Represents base class for any item
    :type _name: str
    :type AC: int
    """
    def __init__(self, base = None, **kwargs):
        self._name = kwargs.get('name', 'noname')
        self._weight = kwargs.get("weight", 10)
        self._hardiness = 10
        # Base item type
        self._base = None
        self._effects = []

    def weight(self):
        return self._weight

    def on_equip(self, combatant):
        pass

    def is_weapon(self):
        return False

    def name(self):
        return self._name