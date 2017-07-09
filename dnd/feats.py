from battle.character import Feat, Character
from battle.combatant import Combatant, AttackDesc
from battle.item import *


class TwoWeaponFighting(Feat):
    def __init__(self):
        Feat.__init__(self, "twf1")

    def apply(self, combatant):
        #events = combatant.event_manager()
        combatant._twf_skill += 1


class ImprovedTwoWeaponFighting(Feat):
    def __init__(self):
        Feat.__init__(self, "twf2")

    def apply(self, combatant):
        #events = combatant.event_manager()
        combatant._twf_skill += 1


class Rage(Feat):
    class Effect(Combatant.StatusEffect):
        def __init__(self, level):
            super(Rage.Effect, self).__init__()
            # Rage level
            self._level = level
            self._stat_bonus = 4

            if self._level == 1:
                self._stat_bonus = 6
            elif self._level == 2:
                self._stat_bonus = 8

        def on_start(self, combatant: Combatant, **kwargs):
            combatant.modify_stat(STAT_STR, self._stat_bonus)
            combatant.modify_stat(STAT_CON, self._stat_bonus)
            combatant.modify_save_will(2)
            self.set_duration(2 + combatant.constitution_modifier())

        def on_finish(self, combatant: Combatant, **kwargs):
            combatant.modify_stat(STAT_STR, -self._stat_bonus)
            combatant.modify_stat(STAT_CON, -self._stat_bonus)
            combatant.modify_save_will(2)
            self.set_duration(2 + combatant.constitution_modifier())

    def __init__(self):
        Feat.__init__(self, "b_rage")

    def apply(self, combatant: Character):
        #combatant.add_feat_action(ActivateEffect(), DURATION_STANDARD)
        pass


class MonkBonusAC(Feat):
    """
    Monk AC bonus
    Provides: AC bonus equal to wisdom_mod + monk_lvl/5
    Works only if character has ARMOR_TYPE_NONE armor
    """
    def __init__(self):
        self._bonus = 0

    def apply(self, combatant:Character):
        events = combatant.event_manager()
        events.on_turn_start += self.on_start
        #combatant.(self, MonkBonusAC.Effect(self))

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        armor = combatant.get_armor_type()
        new_bonus = self._bonus
        if armor == Armor.ARMOR_TYPE_NONE:
            mlevels = combatant.get_class_level("monk")
            new_bonus = math.floor(mlevels / 5) + combatant.wisdom_modifier()
        else:
            new_bonus = 0

        delta = new_bonus - self._bonus
        # Apply the change
        if delta != 0:
            self._bonus += delta
            combatant.modify_ac_dodge(delta)


class CombatReflexes(Feat):
    """
    Combat Reflexes
    Provides: Can execute attacks of opportinuty up to a dex modifier
    """
    def __init__(self):
        super(CombatReflexes, self).__init__("Combat Reflexes")
        self._bonus_aoo = 0

    def apply(self, combatant:Character):
        events = combatant.event_manager()
        events.on_turn_start += self.on_start
        events.on_change_dex += self.on_dex_changed

    def on_dex_changed(self, combatant, effect, old, new):
        mod_new = ability_modifier(new)
        mod_old = ability_modifier(old)
        delta = mod_new - mod_old
        combatant._opportunity_attacks += delta

    def on_start(self, combatant):
        self._bonus_attacks = max(combatant.dexterity_modifier(), 1)
        combatant._opportunity_attacks = self._bonus_attacks


class DeftOpportunist(Feat):
    """
    Deft opportunist
    Provides: "You get a +4 bonus on attack rolls when making attacks of opportunity."
    """
    def __init__(self):
        super(DeftOpportunist, self).__init__("Deft Opportunist")
        "Prerequisite: Combat Reflexes (PH) , DEX 15,"
        self.description = "[General]\nYou are prepared for the unexpected."
        self.description_benefit = "You get a +4 bonus on attack rolls when making attacks of opportunity."

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_calc_attack += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        if desc.opportunity:
            print("%s is using feat %s" % (combatant.get_name(), self.name))
            desc.attack += 4


class InsightfulStrike(Feat):
    def __init__(self):
        super(InsightfulStrike, self).__init__("Insightful strike")

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_calc_attack += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        mod = combatant.intellect_modifier()
        if mod > 0:
            desc.damage.add_die(1,mod)


class WeaponFinesse(Feat):
    """
    Can replace strength modifier by dexterity modifier for melee attacks
    """
    def __init__(self):
        super(WeaponFinesse, self).__init__("WeaponFinesse")

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_calc_attack += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        dex_mod = combatant.dexterity_modifier()
        str_mod = combatant.strength_modifier()
        weapon = desc.weapon

        if desc.is_melee() and dex_mod > str_mod and weapon.is_finessable(combatant):
            bonus = dex_mod - str_mod
            desc.attack += bonus


class WeaponFocus(Feat):
    def __init__(self, weapon):
        super(WeaponFocus, self).__init__("Weapon focus")
        self._weapon = weapon.get_base_root()

    def apply(self, combatant: Combatant):
        combatant.event_manager().on_calc_attack += self.on_calculate_attack

    def on_calculate_attack(self, combatant, desc: AttackDesc):
        if self._weapon == desc.weapon.get_base_root():
            desc.attack += 1


class FlurryOfBlows:
    def __init__(self):
        pass