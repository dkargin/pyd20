from battle.combatant import Combatant
from .item import Item

class Armor(Item):
    """
    Represents armor
    :type _name: str
    :type AC: int
    """
    def __init__(self, base = None, **kwargs):
        Item.__init__(self, base, **kwargs)
        self.AC = kwargs.get("AC", 0)
        self._max_dex = kwargs.get("dex", 100)
        # Base item type
        self.check_penalty = kwargs.get("check", 0)
        self.speed = kwargs.get("speed", 0)
        # Arcane spell failure
        self.arcane_fail = kwargs.get('arcane_fail', 0)
        self._enchantment = 0
        self._deflection_bonus = 0
        self._cover = kwargs.get('cover', False)

    def get_dex_bonus(self, dex):
        return min(self._max_dex, dex)

    def on_equip(self, combatant: Combatant):
        combatant.modify_ac_armor(self.AC + self._enchantment)
        combatant.modify_ac_dex(self._max_dex)


# Default armors
padded = Armor(name='Padded', AC=1, dex=8, check=0, arcane_fail=5, weight=10)
leather = Armor(name='Leather', AC=2, dex=6, check=0, arcane_fail=10, weight=15)
studded_leather = Armor(name='Studded leather', AC=3, dex=5, check=1, arcane_fail=15, weight=20)
chain_shirt = Armor(name='Chain shirt', AC=4, dex=4, check=2, arcane_fail=20, weight=25)
hide = Armor(name='Hide', AC=3, dex=4, check=3, arcane_fail=20, weight=25)
scale_mail = Armor(name='Scale mail', AC=4, dex=3, check=4, arcane_fail=25, weight=30)
chainmail = Armor(name='Chain mail', AC=5, dex=2, check=5, arcane_fail=30, weight=40)
breastplate = Armor(name='Breastplate', AC=5, dex=3, check=4, arcane_fail=25, weight=30)
splint_mail = Armor(name='Splint mail', AC=6, dex=0, check=7, arcane_fail=40, weight=45)
banded_mail = Armor(name='Banded bail', AC=6, dex=1, check=6, arcane_fail=35, weight=35)
half_plate = Armor(name='Half plate', AC=7, dex=0, check=7, arcane_fail=40, weight=50)
full_plate = Armor(name='Full plate', AC=8, dex=1, check=6, arcane_fail=35, weight=50)

# Default shields
buckler = Armor(name='Buckler', AC=1, check=6, arcane_fail=5, weight=5)
lightshield_wood = Armor(name='Light wooden shield', AC=1, check=1, arcane_fail=5, weight=5)
lightshield_steel = Armor(name='Light steel shield', AC=1, check=1, arcane_fail=5, weight=6)
heavyshield_wood = Armor(name='Heavy wooden shield', AC=2, check=2, arcane_fail=15, weight=10)
heavyshield_steel = Armor(name='Heavy steel shield', AC=2, check=2, arcane_fail=15, weight=15)
tower_shield = Armor(name='Tower shield', AC=4, dex=2, check=10, arcane_fail=35, weight=45)


