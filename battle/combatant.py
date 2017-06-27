from core import *
import dice
import dnd.weapon


# Attack description
class AttackDesc:
    def __init__(self, weapon, on_hit=None, **kwargs):
        self.attack = kwargs.get('attack', 0)
        self.damage = kwargs.get('damage', dice.Dice())
        self.weapon = weapon
        self.touch = kwargs.get('touch', False)
        self.on_hit = on_hit

    def text(self):
        dmg_min, dmg_max = self.damage.get_range()
        weapon_name = self.weapon._name if self.weapon is not None else "null weapon"
        return "attack with %s, roll=%d dam=%s->%d-%d" % (weapon_name, self.attack, self.damage.to_string(), dmg_min, dmg_max)

    def __repr__(self):
        return self.text()


# Contains current combatant characteristics
# Should be as flat as possible for better performance
class Combatant(object):
    def __init__(self, name, **kwargs):
        self._name = name
        self._current_initiative = 0

        # Current tile coordinates
        self.X = 0
        self.Y = 0

        # Current visual coordinates. Most of time it is equal to tile coordinates
        self.visual_X = 0.0
        self.visual_Y = 0.0

        self._faction = "none"

        self._stats = [10, 10, 10, 10, 10, 10]

        # List of current status effects, mapping effect->duration
        self._status_effects = {}
        self._experience = 0
        self._alignment = 0
        self._BAB = 0

        # Base max hp
        self._health_max = 0
        # Temporary HP, mappinf from effect to hp
        self._health_temporary = {}
        self._health = 0
        self._brain = None

        # Save value from classes
        self._save_fort_base = 0
        self._save_ref_base = 0
        self._save_will_base = 0

        # Active attack styles
        self._attack_styles = []
        # Armor class
        self._AC = 10
        self._ac_armor = 0
        self._ac_dodge = 0
        self._ac_natural = 0
        self._ac_deflection = 0
        self.move_speed = 30
        # Attack bonus for chosen maneuver/style
        self._attack_bonus_style = 0
        # Damage bonus can differ for each weapon
        self._damage_bonus_style = 0
        # Body size, in tiles
        self._size = 1
        # Precalculated full round attack set
        self._weapon_strikes = []
        self._natural_strikes = {}
        self._additional_strikes = {}

        self._carry_weight = 0
        self._carry_weight_limit = 0
        self._equipped = {}
        self._spell_failure = 0
        self._armor_check_penalty = 0
        self._max_dex_ac = 100
        self._opportunity_attacks = 1
        self._opportunities_used = []

        self._has_insightfull_strike = False
        self._has_finisse = False
        self._has_zen_archery = False
        self._twf_skill = 0

        self._feats = []
        self._events = DnDEventManager()

        brain = kwargs.get('brain', None)
        self.set_brain(brain)

    # Recalculate internal data
    def recalculate(self):
        self._health = self._health_max
        self._ac_armor = 0
        self._ac_deflection = 0
        self._ac_natural = 0
        self._max_dex_ac = 0

        for slot, item in self._equipped.items():
            item.on_equip(self)

    def __repr__(self):
        return "<" + self.get_name() + ">"

    def modify_ac_armor(self, mod):
        self._ac_armor += mod

    def modify_ac_dodge(self, mod):
        self._ac_armor += mod

    def modify_ac_dex(self, mod):
        self._max_dex_ac = min(self._max_dex_ac, mod)

    def modify_stat(self, stat, value, source=None):
        self._stats[stat] += int(value)
        if stat == STAT_CON:
            self._temp_hp[source] = self.level() * value

    def remove_stat_mod(self, stat, source):
        if stat == STAT_CON:
            if source in self._temp_hp:
                self._temp_hp


    def get_name(self):
        return self._name

    def get_turn_state(self):
        state = TurnState(self)
        return state

    # Wear an item
    # returns true if item is changed
    def wear_item(self, item, slot):
        if slot in self._equipped:
            return False
        self._equipped[slot] = item
        item.on_equip(self)
        #if self._armor is not None:
        #    self._carry_weight_limit -= self._armor.weight()
        self._carry_weight_limit += item.weight()

    # Get armor class
    def get_AC(self, target):
        AC = self._AC + self._ac_deflection + self._ac_dodge + self._ac_natural + self._ac_armor
        dex = self.dexterity_mofifier()
        AC += min(dex, self._max_dex_ac)
        return AC

    def get_touch_ac(self, target):
        AC = self._AC + self._ac_deflection + self._ac_dodge
        dex = self.dexterity_mofifier()
        AC += min(dex, self._max_dex_ac)
        return AC

    def recieve_damage(self, damage):
        self._health -= damage
        return self._health

    # Link brain
    def set_brain(self, brain):
        if brain == self._brain:
            return
        # Detach old brain
        if self._brain is not None:
            self._brain.slave = None
        # Attach new brain
        if brain is not None:
            brain.slave = self
        self._brain = brain

    # Execute an attack
    def do_attack(self, attack_desc):
        pass

    # Calculate total weapon reach
    def total_reach(self):
        reach = self._size
        # TODO: add weapon modifier
        return reach

    # Set combatant faction
    def set_faction(self, faction):
        self._faction = faction

    def get_faction(self):
        return self._faction

    # Override current stats
    def set_stats(self, str, dex, con, int, wis, cha):
        self._stats = [str, dex, con, int, wis, cha]

    def print_character(self):
        text = "Name: %s of %s\n" % (self.get_name(), str(self.get_faction()))
        text+= "STR=%d;DEX=%d;CON=%d;INT=%d;WIS=%d;CHA=%d\n"%tuple(self._stats)
        text+= "HP=%d/%d AC=%d ATT=%d\n" % (self.health(), self._health_max, self.get_AC(None), self.get_attack())
        text+= "fort=%d ref=%d will=%d\n" % (self.save_fort(), self.save_ref(), self.save_will())

        chain = self.generate_bab_chain()
        if len(chain) > 0:
            text+= "Cycle: \n"
            for strike in chain:
                text += "\t%s\n" % strike.text()
        return text

    # Return effective health
    def health(self):
        hp = self._health
        for effect, value in self._health_temporary:
            hp += value
        return hp

    # Get current attack bonus
    def get_attack(self, target=None):
        return self._BAB + self.strength_modifier()

    def get_main_weapon(self, default=None) -> dnd.weapon.Weapon:
        return self._equipped.get(ITEM_SLOT_MAIN, default)

    def get_offhand_weapon(self, default=None)-> dnd.weapon.Weapon:
        return self._equipped.get(ITEM_SLOT_OFFHAND, default)

    # Fill in attack for specified weapon and wield
    def generate_attack(self, attack, weapon, twohanded, target, **kwargs):
        damage = weapon.damage(self, target)
        damage_mod = 0
        str_mod = self.strength_modifier()

        if weapon.is_light(self) and not twohanded:
            damage_mod += int(str_mod / 2)
            if self._has_insightfull_strike and self.intellect_mofifier() > 0:
                damage_mod += self.intellect_mofifier()
        elif twohanded:
            damage_mod += int(str_mod * 1.5)
        else:
            damage_mod += int(str_mod)

        if self._has_finisse:
            attack += max(str_mod, self.dexterity_mofifier())
        else:
            attack += str_mod
        '''
        Damage bonus types:
        str/2, str, str3/2
        int, wis,
        '''
        if damage_mod != 0:
            damage.add_die(1, int(damage_mod))

        # For all effects
        desc = AttackDesc(weapon, attack=attack, damage=damage, **kwargs)
        self._events.modify_attack_desc(self, target, desc)
        return desc
    # Generate attack chain for full attack action
    def generate_bab_chain(self, target = None, **kwargs):
        attack_chain = []
        bab = self._BAB
        touch=kwargs.get('touch')
        weapon = self.get_main_weapon()
        twohanded = weapon.is_twohanded()
        weapon_offhand = self.get_offhand_weapon()
        two_weapon_fighting = False
        attack_bonus_style = self._attack_bonus_style

        if weapon_offhand is not None and weapon_offhand.is_weapon():
            twohanded = False
            two_weapon_fighting = True
            attack_bonus_style -= (4 if weapon_offhand.is_light(self) else 6)
            if self._twf_skill > 0:
                attack_bonus_style += 2

        # Get attacks from main slot
        while bab >= 0:
            attack = bab + attack_bonus_style
            desc = self.generate_attack(attack, weapon, twohanded, target)
            attack_chain.append(desc)
            bab -= 5

        twf_attacks = self._twf_skill+1 if two_weapon_fighting else 0
        bab = self._BAB
        if self._twf_skill == 0:
            attack_bonus_style -= 4

        while twf_attacks > 0:
            desc = self.generate_attack(bab + attack_bonus_style, weapon_offhand, False, target)
            attack_chain.append(desc)
            twf_attacks -= 1
            bab -= 5

        return attack_chain

    # Check if combatant is absolutely dead
    def is_dead(self):
        return self._health <= -10

    def is_consciousness(self):
        return self._health > 0

    # If combatant is making turns
    def is_active(self):
        return self.is_consciousness()

    def add_feat(self, feat):
        self._feats.append(feat)
        feat.apply(self)

    # Any feat is implemented by activating certain 'effects' on a combatant
    def allow_effect_activation(self, effect, source = None):
        pass

    def ability(self, abilty_name):
        """
        returns the value of the ability with the given name

        :param str abilty_name: The name of the ability
        :rtype: int
        """
        return self.__ABILITIES[abilty_name.lower()]()

    def constitution(self):
        return self._stats[STAT_CON]

    def charisma(self):
        return self._stats[STAT_CHA]  # + age_modifier

    def dexterity(self):
        return self._stats[STAT_DEX]

    def intellect(self):
        return self._stats[STAT_INT]  # + age_modifier

    def strength(self):
        return self._stats[STAT_STR]  # - age_modifier

    def wisdom(self):
        return self._stats[STAT_WIS]  # + age_modifier

    def constitution_mofifier(self):
        """
        returns the constitution modifier

        :rtype: int
        """
        return ability_modifier(self.constitution())

    def charisma_mofifier(self):
        """
        returns the charisma modifier

        :rtype: int
        """
        return ability_modifier(self.charisma())

    def dexterity_mofifier(self):
        """
        returns the dexterity modifier

        :rtype: int
        """
        return ability_modifier(self.dexterity())

    def intellect_mofifier(self):
        """
        returns the intellect modifier

        :rtype: int
        """
        return ability_modifier(self.intellect())

    def strength_modifier(self):
        """
        returns the strength modifier

        :rtype: int
        """
        return ability_modifier(self.strength())

    def wisdom_mofifier(self):
        """
        returns the wisdom modifier

        :rtype: int
        """
        return ability_modifier(self.wisdom())

    def reset_round(self):
        """
        Resets the round for this combatant
        """
        self._is_flat_footed = False
        self._action_points = 3
        self._current_initiative = self.initiative()


    # Return combatant coordinates
    def coords(self):
        return (self.X, self.Y)

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

    # Get generator
    def gen_actions(self, battle, state):
        if self._brain is not None:
            # Retur
            yield from self._brain.make_turn(battle, state)

    # Overriden by character
    def get_name(self):
        return self._name

    def on_save_throw(self, DC):
        # TODO: implement it
        return False

    def save_will(self):
        return self._save_fort_base + self.wisdom_mofifier()

    def save_ref(self):
        return self._save_fort_base + self.dexterity_mofifier()

    def save_fort(self):
        return self._save_fort_base + self.constitution_mofifier()


# Encapsulates current turn state
class TurnState(object):
    def __init__(self, combatant):
        self.combatant = combatant
        self.moves_left = combatant.move_speed
        self.move_actions = 1
        self.standard_actions = 1
        self.fullround_actions = 1
        self.move_5ft = 1
        self.swift_actions = 1
        self.opportunity_attacks = 1
        # Attacked opportunity targets
        self.opportunity_targets = []

    # Use move action
    def use_move(self):
        self.move_5ft = 0
        self.fullround_actions = 1

    # Use standard action
    def use_standard(self):
        self.standard_actions = 0
        self.fullround_actions = 0

    # Use fullround action
    def use_full_round(self):
        self.standard_actions = 0
        self.fullround_actions = 0
        self.move_actions = 0

    # Called on start of the turn
    def on_round_start(self):
        self.moves_left = self.combatant.move_speed
        self.move_actions = 1
        self.standard_actions = 1
        self.fullround_actions = 1
        self.move_5ft = 1
        self.swift_actions = 1
        self.opportunity_attacks = 1

    # Called when combatant's turn is ended
    def on_round_end(self):
        # Attacked opportunity targets
        self.opportunity_targets = []
        self.opportunity_attacks = 1


# Any sort of effect, that can change stat or any mechanic
class StatusEffect(object):
    def __init__(self):
        self._duration = -1

    # Get effect name
    def name(self):
        return "unknown"

    # Get effect duration
    def get_duration(self):
        return self._duration

    def set_duration(self, duration):
        self._duration = duration

    # Called when effect has started
    def on_start(self, combatant, **kwargs):
        pass

    # Called when effect has finished
    def on_finish(self, combatant, **kwargs):
        pass


class StatusRage(StatusEffect):
    def __init__(self, level):
        StatusEffect.__init__(self)
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


# Should it be any different from effect?
class AttackStyle(object):
    def __init__(self):
        pass

    def on_start(self, combatant):
        pass

    def on_finish(self, combatant):
        pass


# Manager for DnD system events
# Stores a number of handlers for each event type
# This used to implement lots of feat overrides
class DnDEventManager:
    def __init__(self):
        # For sneak attack, all passive targets,
        self._attack_desc = []
        # Events that fired on round start
        self._round_start = []
        # Events that fired when combatant is hit
        self._on_get_hit = []
        # Called when effect is applied
        self._on_effect_apply = []

        self._on_save_will = []
        self._on_save_fort = []
        self._on_save_ref = []

    def subscribe_attack_desc(self, handler):
        if handler not in self._attack_desc:
            self._attack_desc.append(self)

    def unsubscribe_attack_desc(self, handler):
        if handler in self._attack_desc:
            self._attack_desc.remove(handler)

    # Called during attack calculation
    def modify_attack_desc(self, combatant: Combatant, target: Combatant, desc: AttackDesc):
        for handler in self._attack_desc:
            handler(combatant, target, desc)

    # Call all handlers for fortitude saving throw
    def on_save_fort(self, combatant, effect, **kwargs):
        for handler in self._on_save_fort:
            handler(combatant, effect, **kwargs)

    # Call all handlers for reflex saving throw
    def on_save_ref(self, combatant, effect, **kwargs):
        for handler in self._on_save_ref:
            handler(combatant, effect, **kwargs)

    # Call all handlers for will saving throw
    def on_save_will(self, combatant, effect, **kwargs):
        for handler in self._on_save_will:
            handler(combatant, effect, **kwargs)

    # Call all handlers for
    def on_get_hit(self, combatant, effect, **kwargs):
        for handler in self._on_get_hit:
            handler(combatant, effect, **kwargs)
