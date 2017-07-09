from .core import *
from battle.dice import *
import battle.item
from .entity import Entity
import copy


class AttackDesc:
    """
    Attack description structure
    Keeps all the data that can describe any sort of attack with d20 roll
    Each AttackDesc passes several stages before actual hit:
        - Attack is generated as part of BAB chain when character starts its turn
        - Picked target for an attack. Target-specific feats apply its effects
        - Resolve attack and on-hit events
        - Apply damage
    """
    def __init__(self, weapon: battle.item.Weapon, **kwargs):
        self.attack = kwargs.get('attack', 0)
        self.damage = kwargs.get('damage', Dice())
        # Diced bonus damage, like sneak attack, elemental damage and so on
        self.bonus_damage = Dice()
        self.damage_multiplier = 1
        self.critical_confirm_bonus = 0
        self.two_handed = kwargs.get('two_handed', False)
        self.weapon = weapon
        self.touch = kwargs.get('touch', False)
        # Attack target
        self.target = None
        self.source = None
        self.opportunity = False
        self.spell = False
        self.ranged = False

    def is_melee(self):
        return not self.ranged

    def copy(self):
        return copy.copy(self)

    def text(self):
        dmg_min, dmg_max = self.damage.get_range()
        weapon_name = self.weapon.name if self.weapon is not None else "null weapon"
        return "attack with %s, roll=%d dam=%s->%d-%d" % \
               (weapon_name, self.attack, str(self.damage), dmg_min, dmg_max)

    def roll_attack(self):
        result = d20.roll()
        return self.attack + result, result

    def roll_damage(self):
        return self.damage.roll()

    def roll_bonus_damage(self):
        return self.bonus_damage.roll()

    # Calculates hit probability
    def hit_probability(self, armor_class):
        delta = 20 + self.attack - armor_class
        if delta < 1:
            delta = 1
        if delta > 19:
            delta = 19
        return delta / 20.0

    # Calculate estimated damage per round
    def estimated_damage(self, target):
        prob = self.hit_probability(target.get_armor_class())
        # TODO: calculate critical damage bonus
        damage = self.damage.mean() + self.bonus_damage.mean()
        return prob * damage

    def is_critical(self, roll):
        return self.weapon.is_critical(roll)

    def get_target(self):
        return self.target

    def update_target(self, target):
        self.target = target

    def __repr__(self):
        return self.text()


# Utility class for storing event subscribers
class SubscriberList:
    def __init__(self):
        self._subscribers = []

    def __iadd__(self, handler):
        if not callable(handler):
            raise ValueError
        if handler not in self._subscribers:
            self._subscribers.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self._subscribers:
            self._subscribers.remove(handler)
        return self

    # Call all subscribers
    def __call__(self, *args, **kwargs):
        for handler in self._subscribers:
            handler(*args, **kwargs)


class Combatant(Entity):
    """
    Combatant class
    Implement common functionality for characters or monsters
    """
    class EventManager:
        """
        Manager for DnD system events
        Stores a number of handlers for each event type
        This used to implement lots of feat overrides
        """
        def __init__(self):
            # For sneak attack, all passive targets,
            # modify_attack_desc(self, combatant: Combatant, target: Combatant, desc: AttackDesc):
            self.on_calc_attack = SubscriberList()
            # Events that fired when combatant rolls critical hit
            # on_roll_crit(self, combatant: Combatant, target: Combatant, desc: AttackDesc):
            self.on_roll_crit = SubscriberList()
            # Events that fired on start of the turn
            # on_turn_start(self, combatant: Combatant):
            self.on_turn_start = SubscriberList()
            # Events that fired on end of the turn
            # on_turn_end(self, combatant: Combatant):
            self.on_turn_end = SubscriberList()
            # Events that fired on end of the round
            # on_round_end(self, combatant: Combatant):
            self.on_round_end = SubscriberList()
            # Events that fired when combatant is hit
            # on_get_hit(self, combatant, effect, **kwargs):
            self.on_get_hit = SubscriberList()
            # Called when effect is applied
            self.on_effect_apply = SubscriberList()

            # Called when character rolls saving throw
            # on_save_will(self, combatant, effect, **kwargs):
            self.on_save_will = SubscriberList()
            # on_save_fort(self, combatant, effect, **kwargs):
            self.on_save_fort = SubscriberList()
            # on_save_ref(self, combatant, effect, **kwargs):
            self.on_save_ref = SubscriberList()
            # on_change_stat(self, combatant, effect, old, new):
            # Called when stats are changed. Some feats produce stat-dependent bonuses, so we need to notify them
            self.on_change_str = SubscriberList()
            self.on_change_dex = SubscriberList()
            self.on_change_con = SubscriberList()
            self.on_change_int = SubscriberList()
            self.on_change_wis = SubscriberList()
            self.on_change_cha = SubscriberList()

    class StatusEffect(object):
        """
        Any sort of effect, that can change stat or any mechanic
        """
        def __init__(self, name):
            self._duration = -1
            self._name = name

        # Get effect name
        @property
        def name(self):
            return self._name

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

    def __init__(self, name, **kwargs):
        Entity.__init__(self, name, **kwargs)

        self._current_initiative = 0
        self._faction = "none"

        self._stats = [10, 10, 10, 10, 10, 10]

        # List of current status effects, mapping effect->duration
        self._status_effects = []
        self._status_flags = set()
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

        self._save_fort_bonus = 0
        self._save_ref_bonus = 0
        self._save_will_bonus = 0


        # Active attack styles
        self._attack_styles = []
        # Armor class
        self._AC = 10
        self._ac_armor = 0
        self._ac_dodge = 0
        self._ac_natural = 0
        self._ac_deflection = 0
        self.move_speed = 30
        # Penalty to move speed
        self._move_penalty = 0
        # Attack bonus for chosen maneuver/style
        self._attack_bonus_style = 0
        # Damage bonus can differ for each weapon
        self._damage_bonus_style = 0
        # Full round attack set
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
        self._opportunity_attacks_max = 1
        self._opportunities_used = []
        self._natural_reach = 1
        self._has_zen_archery = False
        self._twf_skill = 0

        self._turn_state = TurnState()

        self._feats = []
        self._events = Combatant.EventManager()

        # Current path. For visualization
        self.path = None

        brain = kwargs.get('brain', None)
        self.set_brain(brain)

    def event_manager(self):
        """
        Get access to event manager
        :return:Combatant.EventManager
        """
        return self._events

    def has_status_flag(self, status):
        return status in self._status_flags

    def add_status_flag(self, status):
        self._status_flags.add(status)

    def remove_status_flag(self, status):
        self._status_flags.remove(status)

    # Recalculate internal data
    def recalculate(self):
        self._health = self._health_max
        self._ac_armor = 0
        self._ac_deflection = 0
        self._ac_natural = 0
        self._max_dex_ac = 100

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

    def add_persistent_effect(self, effect, effect_on, effect_off):
        self._status_effects.append(effect)

    def get_armor_type(self):
        armor = self._equipped.get(ITEM_SLOT_ARMOR, None)
        if armor is None:
            return ARMOR_TYPE_NONE
        return armor.armor_type()

    def remove_stat_mod(self, stat, source):
        if stat == STAT_CON:
            if source in self._temp_hp:
                self._temp_hp

    def get_turn_state(self):
        strikes = self.generate_bab_chain()
        self._turn_state.set_attacks(strikes)
        # Use the first strike for AoO
        self._turn_state.attack_AoO = strikes[0]
        return self._turn_state

    # Called on start of the turn
    def on_round_start(self):
        state = self._turn_state

        if self.has_status_flag(STATUS_HEAVY_ARMOR):
            state.move_penalty = 10

        state.moves_left = self.move_speed - self._move_penalty

        state.move_actions = 1
        state.standard_actions = 1
        state.full_round_actions = 1
        state.move_5ft = 1
        state.swift_actions = 1
        #self.opportunity_attacks = 1
        self._opportunities_used = []
        self._ac_dodge = 0
        self._events.on_turn_start(self)
        pass

    # Called when combatant's turn is ended
    def on_round_end(self):
        state = self._turn_state
        # Attacked opportunity targets
        # Clean up attack sequence
        state.attacks = []
        self._events.on_turn_end(self)

    # Wear an item
    # returns true if item is changed
    def wear_item(self, item, slot):
        if slot in self._equipped:
            return False
        self._equipped[slot] = item
        item.on_equip(self)
        self._carry_weight_limit += item.weight()

    def opportunities_left(self):
        return self._opportunity_attacks - len(self._opportunities_used)

    # Use opportunity attack
    def use_opportunity(self, desc: AttackDesc):
        self._opportunities_used.append(desc)

    def calculate_attack_of_opportunity(self, target):
        desc = self._turn_state.attack_AoO.copy()
        desc.update_target(target)
        desc.opportunity = True
        self._events.on_calc_attack(self, desc)
        self.use_opportunity(desc)
        return desc

    def respond_provocation(self, battle, combatant, action=None):
        if self._brain is not None:
            yield from self._brain.respond_provocation(battle, combatant, action)

    # Get armor class
    def get_armor_class(self, target=None):
        armor_class = self._AC + self._ac_deflection + self._ac_dodge + self._ac_natural + self._ac_armor
        dex = self.dexterity_modifier()
        armor_class += min(dex, self._max_dex_ac)
        return armor_class

    def get_touch_armor_class(self, target=None):
        armor_class = self._AC + self._ac_deflection + self._ac_dodge
        dex = self.dexterity_modifier()
        armor_class += min(dex, self._max_dex_ac)
        return armor_class

    def receive_damage(self, damage, source):
        self._events.on_get_hit(self, source, damage)
        self._health -= damage

        print("%s damages %s for %d damage, %d HP left" % (source.name, self.name, damage, self._health))

        if self._health <= -10:
            print("%s is dead" % self.name)
        elif self._health < 0:
            print("%s is unconsciousness" % self.name)
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

    # Check if combatant has near reach
    def has_reach_near(self):
        weapon = self.get_main_weapon()
        if weapon is not None and weapon.has_reach_near():
            return True
        return False

    # Check if combatant has far reach
    def has_reach_far(self):
        weapon = self.get_main_weapon()
        if weapon is not None and weapon.has_reach_far():
            return True
        return False

    def natural_reach(self):
        return self._natural_reach

    @property
    def save_fort(self):
        return self._save_fort_base + self._save_fort_bonus

    @property
    def save_ref(self):
        return self._save_ref_base + self._save_ref_bonus

    @property
    def save_will(self):
        return self._save_will_base + self._save_will_bonus

    # Calculate total weapon reach
    def total_reach(self):
        reach = self._natural_reach
        weapon = self.get_main_weapon()
        if weapon is not None and weapon.has_reach():
            reach *= 2
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
        text += "STR=%d;DEX=%d;CON=%d;INT=%d;WIS=%d;CHA=%d\n" % tuple(self._stats)
        text += "HP=%d/%d AC=%d ATT=%d\n" % (self.health(), self._health_max, self.get_armor_class(None), self.get_attack())
        text += "fort=%d ref=%d will=%d\n" % (self.save_fort(), self.save_ref(), self.save_will())

        chain = self.generate_bab_chain()
        if len(chain) > 0:
            text += "Cycle: \n"
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

    def get_main_weapon(self, default=None) -> battle.item.Weapon:
        return self._equipped.get(ITEM_SLOT_MAIN, default)

    def get_offhand_weapon(self, default=None)-> battle.item.Weapon:
        return self._equipped.get(ITEM_SLOT_OFFHAND, default)

    # Fill in attack for specified weapon and wield
    def generate_attack(self, attack, weapon, two_handed, target, **kwargs):
        damage = weapon.damage(self, target)
        damage_mod = 0
        str_mod = self.strength_modifier()

        if weapon.is_light(self) and not two_handed:
            damage_mod += int(str_mod / 2)
        elif two_handed:
            damage_mod += int(str_mod * 1.5)
        else:
            damage_mod += int(str_mod)

        """
        if self._has_finisse:
            attack += max(str_mod, self.dexterity_modifier())
        else:
            attack += str_mod
        """

        if damage_mod != 0:
            damage.add_die(1, int(damage_mod))

        # For all effects
        desc = AttackDesc(weapon, attack=attack, damage=damage, two_handed=two_handed, **kwargs)
        self._events.on_calc_attack(self, desc)
        return desc

    # Generate attack chain for full attack action
    def generate_bab_chain(self, target=None, **kwargs):
        attack_chain = []
        bab = self._BAB
        weapon = self.get_main_weapon()
        two_handed = weapon.is_two_handed()
        weapon_offhand = self.get_offhand_weapon()
        two_weapon_fighting = False
        attack_bonus_style = self._attack_bonus_style

        if weapon_offhand is not None and weapon_offhand.is_weapon():
            two_handed = False
            two_weapon_fighting = True
            attack_bonus_style -= (4 if weapon_offhand.is_light(self) else 6)
            if self._twf_skill > 0:
                attack_bonus_style += 2

        # Get attacks from main slot
        while bab >= 0:
            attack = bab + attack_bonus_style
            desc = self.generate_attack(attack, weapon, two_handed, target, **kwargs)
            attack_chain.append(desc)
            bab -= 5

        twf_attacks = self._twf_skill if two_weapon_fighting else 0
        bab = self._BAB
        if self._twf_skill == 0:
            attack_bonus_style -= 4

        while twf_attacks > 0:
            desc = self.generate_attack(bab + attack_bonus_style, weapon_offhand, False, target, **kwargs)
            attack_chain.append(desc)
            twf_attacks -= 1
            bab -= 5

        return attack_chain

    # Check if combatant is absolutely dead
    # There are some feats, that can override this condition
    def is_dead(self):
        return self._health <= -10

    def is_consciousness(self):
        return self._health > 0

    # If combatant is making turns
    def is_active(self):
        return self.is_consciousness()

    def add_feat(self, feat):
        """
        Adds feat to known feat list.
        This function does not care for feat requirements
        :param feat:
        """
        self._feats.append(feat)
        feat.apply(self)

    # Any feat is implemented by activating certain 'effects' on a combatant
    def allow_effect_activation(self, effect, source=None):
        pass

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

    def constitution_modifier(self):
        """
        returns the constitution modifier

        :rtype: int
        """
        return ability_modifier(self.constitution())

    def charisma_modifier(self):
        """
        returns the charisma modifier

        :rtype: int
        """
        return ability_modifier(self.charisma())

    def dexterity_modifier(self):
        """
        returns the dexterity modifier

        :rtype: int
        """
        return ability_modifier(self.dexterity())

    def intellect_modifier(self):
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

    def wisdom_modifier(self):
        """
        returns the wisdom modifier

        :rtype: int
        """
        return ability_modifier(self.wisdom())

    def reset_round(self):
        """
        Resets the round for this combatant
        """
        self._current_initiative = self.initiative()

    def current_initiative(self):
        """
        Returns the last rolled initiative
        :rtype: int
        """
        return self._current_initiative

    def initiative(self):
        """
        Calculates the initiative

        :rtype: int
        """
        return d20.roll() + self.dexterity_modifier()

    # Get generator
    def gen_brain_actions(self, battle):
        if self._brain is not None:
            yield from self._brain.make_turn(battle)

    def save_will(self):
        return self._save_fort_base + self.wisdom_modifier()

    def save_ref(self):
        return self._save_fort_base + self.dexterity_modifier()

    def save_fort(self):
        return self._save_fort_base + self.constitution_modifier()


# Encapsulates current turn state
class TurnState(object):
    def __init__(self):
        self.moves_left = 0
        self.move_actions = 1
        self.standard_actions = 1
        self.full_round_actions = 1
        self.move_5ft = 1
        self.swift_actions = 1
        self.made_attack = 0
        # Available attacks
        self.attacks = []
        # Attack to be used for AoO
        self.attack_AoO = []

    def set_attacks(self, attacks):
        self.attacks = attacks

    # Use attack from generated attack list
    def use_attack(self):
        if len(self.attacks) > 0:
            attack = self.attacks.pop(0)
            self.made_attack += 1
            self.use_standard(attack=True)
            return attack
        return None

    # Use move action
    def use_move(self, real_move = True):
        if real_move:
            self.move_5ft = 0
        self.full_round_actions = 1

    # Returns true if character has attack actions
    def can_attack(self):
        return (self.full_round_actions > 0 or self.standard_actions > 0) and len(self.attacks) > 0

    def can_move(self):
        return self.moves_left > 0 and self.move_actions > 0

    def can_5ft_step(self):
        return self.move_5ft > 0

    # Use standard action
    def use_standard(self, attack=False):
        self.standard_actions = 0
        if not attack:
            self.full_round_actions = 0
            self.made_attack = 1

    # Use full round action
    def use_full_round(self):
        self.standard_actions = 0
        self.full_round_actions = 0
        self.move_actions = 0

    def complete(self):
        return not self.can_attack() and not self.can_move()


# Should it be any different from effect?
class AttackStyle(object):
    def __init__(self):
        pass

    def on_start(self, combatant):
        pass

    def on_finish(self, combatant):
        pass

