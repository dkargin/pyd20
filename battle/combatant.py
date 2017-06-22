from core import *

# Contains current combatant characteristics
# Should be as flat as possible for better performance
class Combatant(object):
    """
    :type _is_flat_footed: bool
    :type _action_points: int
    :type _current_initiative: int
    """
    def __init__(self):
        self._current_initiative = 0
        self.X = 0
        self.Y = 0
        self._stats = [10, 10, 10, 10, 10, 10]
        self._status_effects = {}
        self._experience = 0
        self._alignment = 0
        self._BAB = 0
        self._health_max = 0
        self._health = 0
        self._brain = None

        # Save value from classes
        self._save_fort_base = 0
        self._save_ref_base = 0
        self._save_will_base = 0
        self._AC = 10
        self.move_speed = 30
        # Attack bonus for chosen maneuver/style
        self._attack_bonus_style = 0
        # Reach, in tiles. Depends on weapon
        self._reach = 1

    # Recalculate internal data
    def recalculate(self):
        self._health = self._health_max

    def get_turn_state(self):
        state = TurnState(self)
        return state

    # Get armor class
    def get_AC(self):
        return self._AC + self.dexterity_mofifier()

    def recieve_damage(self, damage):
        self._health -= damage
        return self._health

    # Link brain
    def set_brain(self, brain):
        self._brain = brain
        brain.slave = self

    # Override current stats
    def set_stats(self, str, dex, con, int, wis, cha):
        self._stats = [str, dex, con, int, wis, cha]

    # Get current attack bonus
    def get_attack(self):
        return self._BAB + self.strength_modifier()

    # Check if combatant is absolutely dead
    def is_dead(self):
        return self._health <= -10

    def is_consciousness(self):
        return self._health > 0

    # If combatant is making turns
    def is_active(self):
        return self.is_consciousness()

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
        return "Unknown"


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
