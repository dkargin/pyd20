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
        self._base = base
        self._effects = []

    def weight(self):
        return self._weight

    def on_equip(self, combatant):
        pass

    def on_remove(self, combatant):
        pass

    def is_weapon(self):
        return False

    def name(self):
        return self._name

    # Get base item
    def get_base_root(self):
        if self._base is None:
            return self
        return self._base.get_base_root()