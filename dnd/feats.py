from battle.character import Feat, Character
from battle.combatant import Combatant, AttackDesc
from battle.core import *


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
            self.set_duration(2 + combatant.constitution_mofifier())

        def on_finish(self, combatant: Combatant, **kwargs):
            combatant.modify_stat(STAT_STR, -self._stat_bonus)
            combatant.modify_stat(STAT_CON, -self._stat_bonus)
            combatant.modify_save_will(2)
            self.set_duration(2 + combatant.constitution_mofifier())

    def __init__(self):
        Feat.__init__(self, "b_rage")

    def apply(self, combatant: Character):
        #combatant.add_feat_action(ActivateEffect(), DURATION_STANDARD)
        pass


class MonkBonusAC(Feat):
    def __init__(self):
        self._bonus = 0

    def apply(self, combatant:Character):
        events = combatant.event_manager()
        events.on_turn_start += self.on_start
        #combatant.(self, MonkBonusAC.Effect(self))

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        armor = combatant.get_armor_type()
        if armor == ARMOR_TYPE_NONE:
            mlevels = combatant.get_class_level("monk")
            newbonus = math.floor(mlevels / 5) + combatant.wisdom_mofifier()
            delta = newbonus - self._bonus
            if delta != 0:
                self._bonus += delta
                combatant.modify_ac_dodge(delta)

class CombatReflexes(Feat):
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
        self._bonus_attacks = max(combatant.dexterity_mofifier(), 1)
        combatant._opportunity_attacks = self._bonus_attacks


class DeftOpportunist(Feat):
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


class FlurryOfBlows:
    def __init__(self):
        pass