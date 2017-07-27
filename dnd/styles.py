from sim.combatant import Combatant

from .skills import SkillTumble


class StyleDefenciveFight(Combatant.StatusEffect):
    def __init__(self):
        super(StyleDefenciveFight, self).__init__("Fighting defencively")
        self.attack_pen = 4
        self.base_value = 2
        self.bonus = 0
        self.applied = 0

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        combatant._attack_bonus_style -= self.attack_pen

        if combatant.skill_levels(SkillTumble) >= 5:
            self.bonus += 1

        self.applied = self.base_value + self.bonus
        combatant.modify_ac_dodge(self.applied)

    # Called when effect has finished
    def on_finish(self, combatant, **kwargs):
        combatant._attack_bonus_style += self.attack_pen
        combatant.modify_ac_dodge(-self.applied)
        self.bonus = 0
        self.applied = 0

    def __str__(self):
        return "fight_defence"


class StyleFlurryOfBlows(Combatant.StatusEffect):
    def __init__(self, penalty=0, attacks=1):
        super(StyleFlurryOfBlows, self).__init__("Flurry of blows")
        self.attack_pen = penalty
        self.add_attacks = attacks
        self._attacks = []

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        combatant._attack_bonus_style -= self.attack_pen
        for a in range(0, self.add_attacks):
            self._attacks.append(combatant.add_bonus_strike(combatant.get_main_weapon(), bab=0))

    # Called when effect has finished
    def on_finish(self, combatant, **kwargs):
        combatant._attack_bonus_style += self.attack_pen
        for strike in self._attacks:
            combatant.expend_attack(strike)

    def __str__(self):
        return "flurry_blows"
