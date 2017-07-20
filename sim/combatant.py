from .core import *
from sim.dice import *
import sim.item
from .entity import Entity
import copy
import animation

from .attackdesc import AttackDesc
from sim.events import AnimationEvent
from .turnstate import TurnState


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
            # Called when attack is prepared
            # handler(self, combatant: Combatant, target: Combatant, desc: AttackDesc):
            self.on_calc_attack = SubscriberList()
            # Called when selected target for opportunity attack
            # handler(self, combatant: Combatant, target: Combatant, desc: AttackDesc):
            #self.on_calc_opportinity_attack = SubscriberList()
            # Called when picked attack target
            self.on_select_attack_target = SubscriberList()
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
            self.on_effect_start = SubscriberList()
            self.on_effect_stop = SubscriberList()

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

        def __repr__(self):
            return str(self)

        def __str__(self):
            return self.name

        def __hash__(self):
            return hash(self.name)

        def __eq__(self, other):
            return self.name == other.name

        def __ne__(self, other):
            # Not strictly necessary, but to avoid having both x==y and x!=y
            # True at the same time
            return not (self == other)

    def __init__(self, name, **kwargs):
        size_type = kwargs.get('csize', SIZE_MEDIUM)
        if 'size' not in kwargs:
            kwargs['size'] = SIZE_CATEGORIES[size_type].tiles

        Entity.__init__(self, name, **kwargs)

        self._size_type = size_type
        self._size_cat = SIZE_CATEGORIES[size_type]
        self._current_initiative = 0
        self._faction = "none"

        self._stats = [10, 10, 10, 10, 10, 10]

        # List of current status effects, mapping effect->duration
        self._status_effects = []
        self._status_flags = set()
        self._experience = 0
        self._alignment = 0
        self._BAB = 0
        self.model = kwargs.get('model', 'naked')
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
        self._move_speed = 30
        self._move_speed_bonus = 0
        # Penalty to move speed
        self._move_penalty = 0
        # Attack bonus for chosen maneuver/style
        self._attack_bonus_style = 0
        self._two_hand_wield = False
        self._many_weapon_wield = False
        # Damage bonus can differ for each weapon
        self._damage_bonus_style = 0
        # Full round attack set
        self._weapon_strikes = []
        self._natural_strikes = {}
        self._additional_strikes = []

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

        self._turn_state = TurnState()

        self._known_styles = set()
        self._active_styles = []

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

    def modify_ac_armor(self, mod, source=None):
        self._ac_armor += mod

    def modify_ac_dodge(self, mod, source=None):
        self._ac_dodge += mod

    def modify_ac_dex(self, mod):
        self._max_dex_ac = min(self._max_dex_ac, mod)

    def modify_movement(self, mod):
        self._move_penalty -= mod

    def modify_stat(self, stat, value, source=None):
        self._stats[stat] += int(value)
        if stat == STAT_CON:
            self._temp_hp[source] = self.level() * value

    def add_persistent_effect(self, effect, effect_on, effect_off):
        self._status_effects.append(effect)

    def get_armor_type(self):
        armor = self._equipped.get(ITEM_SLOT_ARMOR, None)
        if armor is None:
            return sim.item.Armor.ARMOR_TYPE_NONE
        return armor.armor_type()

    def remove_stat_mod(self, stat, source):
        if stat == STAT_CON:
            if source in self._temp_hp:
                self._temp_hp

    def get_turn_state(self):
        # TODO: should refactor it ?
        strikes = self.generate_bab_chain()
        self._turn_state.set_attacks(strikes)
        # Use the first strike for AoO
        self._turn_state.attack_AoO = strikes[0]
        return self._turn_state

    def modify_move_speed(self, mod, source=None):
        self._move_speed_bonus += mod

    @property
    def move_speed(self):
        return self._move_speed + self._move_speed_bonus - self._move_penalty

    # Called on start of the turn
    def on_turn_start(self, battle, brain=True):
        state = self._turn_state

        # Stop styles from previous turns
        for style in self._active_styles:
            style.on_finish(self)

        self._attack_bonus_style = 0
        self.check_weapon_wield()

        if self.has_status_flag(STATUS_HEAVY_ARMOR):
            self._move_penalty = 10

        state.start_turn(self)

        self._opportunities_used = []
        self._events.on_turn_start(self)
        if brain:
            self._brain.prepare_turn(battle)

    # Called when combatant's turn is ended
    def on_turn_end(self):
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

    def activate_style(self, style):
        self._active_styles.append(style)
        style.on_start(self)

    def deactivate_style(self, style):
        style.on_finish(self)
        self._active_styles.remove(style)

    def opportunities_left(self):
        return self._opportunity_attacks - len(self._opportunities_used)

    # Use opportunity attack
    def use_opportunity(self, desc):
        self._opportunities_used.append(desc)

    def calculate_attack_of_opportunity(self, target):
        desc = self._turn_state.attack_AoO.copy()
        desc.update_target(target)
        desc.opportunity = True
        self.use_opportunity(desc)
        return desc

    def respond_provocation(self, battle, combatant, action=None):
        if self._brain is not None:
            yield from self._brain.respond_provocation(battle, combatant, action)

    # Get armor class
    def get_armor_class(self, target=None):
        armor_class = self._AC + self._ac_deflection + self._ac_dodge + self._ac_natural + self._ac_armor
        if self._size_cat is not None:
            armor_class += self._size_cat.ac_mod
        dex = self.dexterity_modifier()
        armor_class += min(dex, self._max_dex_ac)
        return armor_class

    def get_touch_armor_class(self, target=None):
        armor_class = self._AC + self._ac_deflection + self._ac_dodge
        if self._size_cat is not None:
            armor_class += self._size_cat.ac_mod
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
        return self._save_fort_base + self._save_fort_bonus + self.constitution_modifier()

    @property
    def save_ref(self):
        return self._save_ref_base + self._save_ref_bonus + self.dexterity_modifier()

    @property
    def save_will(self):
        return self._save_will_base + self._save_will_bonus + self.wisdom_modifier()

    def modify_save_fort(self, mod, base=False):
        if base:
            self._save_fort_base += mod
        else:
            self._save_fort_bonus += mod

    def modify_save_ref(self, mod, base=False):
        if base:
            self._save_ref_base += mod
        else:
            self._save_ref_bonus += mod

    def modify_save_will(self, mod, base=False):
        if base:
            self._save_will_base += mod
        else:
            self._save_will_bonus += mod

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
        text += "HP=%d/%d AC=%d ATT=%d\n" % (self.health, self.health_max, self.get_armor_class(None), self.get_attack())
        text += "fort=%d ref=%d will=%d\n" % (self.save_fort, self.save_ref, self.save_will)

        armor = self._equipped.get(ITEM_SLOT_ARMOR, None)
        shield = self._equipped.get(ITEM_SLOT_OFFHAND, None)

        if armor is not None:
            text += "Protected by %s" % str(armor)
            if shield is not None and shield.is_shield():
                text += " and %s\n" % str(shield)
            else:
                text += "\n"

        chain = self.generate_bab_chain()
        if len(chain) > 0:
            text += "Cycle: \n"
            for strike in chain:
                text += "\t%s\n" % strike.text()
        return text

    # Return effective health
    @property
    def health(self):
        hp = self._health
        for effect, value in self._health_temporary:
            hp += value
        return hp

    @property
    def health_max(self):
        return self._health_max

    # Add bonus attack, from feat, style or status effect
    def add_bonus_strike(self, weapon, source=None, **kwargs):
        attack = kwargs.get('attack', 0)
        if 'bab' in kwargs:
            attack = self._BAB + kwargs['bab'] + self._attack_bonus_style
        desc = self.generate_attack(attack, weapon, target=None, **kwargs)
        self._additional_strikes.append(desc)
        return desc

    # Get current attack bonus
    def get_attack(self, target=None):
        return self._BAB + self.strength_modifier()

    def get_main_weapon(self, default=None) -> sim.item.Weapon:
        return self._equipped.get(ITEM_SLOT_MAIN, default)

    def get_offhand_weapon(self, default=None)-> sim.item.Weapon:
        return self._equipped.get(ITEM_SLOT_OFFHAND, default)

    # Fill in attack for specified weapon and wield
    def generate_attack(self, attack, weapon, target, **kwargs):
        """
        :param attack: attack bonus, bab+circumstances
        :param weapon: used weapon
        :param target: attack target. Can be unavailable at this stage
        :param kwargs: additional parameters
        :rtype: AttackDesc generated attack description
        """
        damage = weapon.damage(self, target)
        damage_mod = 0
        str_mod = self.strength_modifier()

        two_handed = self._two_hand_wield
        ranged = weapon.is_ranged()

        if weapon.is_light(self) and not two_handed:
            damage_mod += int(str_mod / 2)
        elif two_handed:
            damage_mod += int(str_mod * 1.5)
        else:
            damage_mod += int(str_mod)

        if damage_mod != 0:
            damage.add_die(1, int(damage_mod))

        if kwargs.get('offhand', False):
            attack -= 4

        if weapon.is_ranged():
            attack += self.dexterity_modifier()
        else:
            attack += self.strength_modifier()

        # For all effects
        desc = AttackDesc(weapon, attack=attack, damage=damage, two_handed=two_handed, ranged=ranged, **kwargs)
        self._events.on_calc_attack(self, desc)
        return desc

    def check_weapon_wield(self):
        """
        Checks weapon wielding style
        """
        two_handed = False
        two_weapon_fighting = False

        weapon = self.get_main_weapon()
        if weapon is not None:
            two_handed = weapon.is_two_handed()
            weapon_offhand = self.get_offhand_weapon()
            if weapon_offhand is not None and weapon_offhand.is_weapon():
                two_handed = False
                two_weapon_fighting = True

        self._two_hand_wield = two_handed
        self._many_weapon_wield = two_weapon_fighting
        if self._many_weapon_wield:
            self._attack_bonus_style -= (4 if weapon_offhand.is_light(self) else 6)

    def generate_bab_chain(self, target=None, **kwargs):
        """
        Generate attack chain for full attack action

        :param target: target to be attacked
        :return: list of AttackDesc
        """
        attack_chain = []
        bab = self._BAB
        weapon = self.get_main_weapon()

        weapon_offhand = self.get_offhand_weapon()
        attack_bonus_style = self._attack_bonus_style

        """
        Two weapon fighting:
        Normal penalties: Main -6     Offhand -10
        Offhand is light: Main -4     Offhand -8    -> add +2 to both attacks
        Two-weapon fighting: Main -4    Offhand -4  -> add +2 to main and +6 to offhand
        """
        # Get attacks from main slot
        while bab >= 0:
            attack = bab + attack_bonus_style
            attack_chain.append(self.generate_attack(attack, weapon, target, **kwargs))
            bab -= 5

        if self._many_weapon_wield:
            attack = self._BAB + attack_bonus_style
            desc = self.generate_attack(attack, weapon_offhand, target, offhand=True, **kwargs)
            attack_chain.append(desc)

        attack_chain.extend(self._additional_strikes)
        self._additional_strikes = []
        return attack_chain

    # Check if combatant is absolutely dead
    # There are some feats, that can override this condition
    def is_dead(self):
        return self._health <= -10

    def is_consciousness(self):
        return self._health >= 0

    def is_prone(self):
        return self.has_status_flag(STATUS_PRONE)

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
        if effect not in self._known_styles:
            self._known_styles.add(effect)

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
        return ability_modifier(self.constitution())

    def charisma_modifier(self):
        return ability_modifier(self.charisma())

    def dexterity_modifier(self):
        return ability_modifier(self.dexterity())

    def intellect_modifier(self):
        return ability_modifier(self.intellect())

    def strength_modifier(self):
        return ability_modifier(self.strength())

    def wisdom_modifier(self):
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

    def _set_attack_target(self, desc, target):
        self._events.on_select_attack_target(self, desc)

        armor_class = target.get_touch_armor_class(target) if desc.touch else target.get_armor_class(target)

        # Apply penalties for being prone
        if target.has_status_flag(STATUS_PRONE):
            if desc.is_melee():
                armor_class -= 4
            if desc.is_ranged():
                armor_class += 4

        if self.has_status_flag(STATUS_PRONE):
            desc.attack -= 4

        return armor_class

    def expend_attack(self, desc):
        if desc in self._turn_state.attacks:
            self._turn_state.attacks.remove(desc)
        if desc in self._additional_strikes:
            self._additional_strikes.remove(desc)

    # Turn generators #

    # Get generator
    def gen_brain_actions(self, battle):
        if self._brain is not None:
            yield from self._brain.make_turn(battle)

    # Action generators #

    # Execute melee strike action
    def do_action_strike(self, battle, desc: AttackDesc):
        # All data is already set. Attack can be resolved right now
        target = desc.get_target()
        armor_class = self._set_attack_target(desc, target)

        roll, crit_confirm_roll = d20.roll(), d20.roll()

        # Roll for critical confirmation
        has_crit = False

        if desc.is_critical(roll):
            self._events.on_roll_crit(desc)
            has_crit = roll_hits(desc.attack + desc.critical_confirm_bonus, crit_confirm_roll, armor_class)

        hit = roll_hits(desc.attack, roll, armor_class)

        if desc.is_melee():
            yield AnimationEvent(animation.MeleeAttackStart(self, target))
        elif desc.is_ranged():
            yield AnimationEvent(animation.RangedAttack(self, target))

        attack_text = "misses"
        total_damage = 0

        if hit:
            damage = desc.roll_damage()
            bonus_damage = desc.roll_bonus_damage()
            if has_crit:
                damage *= desc.weapon.crit_mult
                attack_text = "critically hits"
            else:
                attack_text = "hits"
            total_damage = damage + bonus_damage

        print("%s %s %s with roll %s" %
              (self.name, attack_text, target.get_name(), desc.attack_roll_info(roll, armor_class)))
        if hit:
            target.receive_damage(damage, self)

        self.expend_attack(desc)
        if desc.is_melee():
            yield AnimationEvent(animation.MeleeAttackFinish(self, target))

    def _make_roll_d20(self, **kwargs):
        # Make d20 roll. There are some feats that allow to reroll result
        # TODO: Brain also can alter some decisions as well
        self._events
        return d20.roll()

    # Execute trip attack  action
    # All data is already set. Attack can be resolved right now
    def do_action_trip_attack(self, battle, desc: AttackDesc):
        target = desc.get_target()
        desc.check = (target._size_type - self._size_type) * 4
        desc.check += self.strength_modifier() - max(target.strength_modifier(), target.dexterity_modifier())

        # 1. Resolve attack. Unarmed attack can provoke AoO
        weapon = desc.weapon

        improved_trip = self.has_status_flag(STATUS_HAS_IMPROVED_TRIP)
        improved_unarmed = self.has_status_flag(STATUS_HAS_IMPROVED_UNARMED)

        provoke = False

        if weapon.is_unarmed() and not (improved_trip or improved_unarmed):
            provoke = True
        elif not (weapon.can_trip() or improved_trip):
            provoke = False

        if provoke:
            battle.provoke_opportunity()

        desc.touch = True

        # 2. Opposed trip check
        armor_class = self._set_attack_target(desc, target)

        roll_attack = self._make_roll_d20()

        hit = roll_hits(desc.attack, roll_attack, armor_class)

        yield AnimationEvent(animation.MeleeAttackStart(self, target))

        roll_info = desc.attack_roll_info(roll_attack, armor_class)

        if hit:
            roll_trip = self._make_roll_d20()
            opposed_roll = target._make_roll_d20(source=self, attack=desc)
            if roll_trip + desc.check > opposed_roll:
                attack_text = "trips"
                target.add_status_flag(STATUS_PRONE)
                print("%s trips %s with roll %s" % (self.name, target.get_name(), roll_info))
            else:
                print("%s fails to trip %s with roll %s" % (self.name, target.get_name(), roll_info))
            print("%s rolls %d, %s rolls %d" % (self.name, roll_trip+desc.check, target.get_name(), opposed_roll))
        else:
            print("%s misses its trip attack %s with roll %s" % (self.name, target.get_name(), roll_info))

        self.expend_attack(desc)

        yield AnimationEvent(animation.MeleeAttackFinish(self, target))

    # Using move action
    def do_action_move_tiles(self, battle, state: TurnState, path):
        # We should iterate all the tiles
        tiles_moved = []
        self.path = path
        # Distance traveled
        traveled = 0
        # [0,1,2,3,4,5,6]
        # [0,0,0,T,T,0,0]
        # Moves: 0->3, 3->4, 4->6
        waypoints = path.get_path()
        while len(waypoints) > 0:
            tile = waypoints.pop(0)
            cost = 5
            tiles_moved.append((tile, cost))
            if battle.position_threatened(self, tile.x, tile.y):
                yield sim.actions.MoveAction(self, state, tiles_moved)
                tiles_moved = []
                traveled = 0

            traveled += cost
            if traveled >= state.moves_left:
                break

        # One last step
        if len(tiles_moved) > 0 is not None:
            yield sim.actions.MoveAction(self, state, tiles_moved)
        pass

