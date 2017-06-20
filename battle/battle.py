import math
import core
from grid import PriorityQueue, Tile, PathFinder
import dice
import logging

# Action durations
DURATION_STANDARD = 0
DURATION_MOVE = 1
DURATION_FULLROUND = 2
DURATION_FREE = 3
DURATION_SWIFT = 4


class Battle(object):
    """
    Models a battle

    :type grid: grid.Grid
    :type _combatants: Combatant[]
    """

    def __init__(self, grid):
        """
        Create an instance of a battle.

        :param Grid grid: The grid the battle takes place on
        """
        self.grid = grid
        self.pathfinder = PathFinder(grid)
        self._combatants = []
        self.round = 0

    def add_combatant(self, combatant, x, y):
        """
        Adds a combatant to the battle. This is typically a Character or a Monster.
        If the grid has no tile at the specified position, the combatant will not
        be added to the battle

        :param Combatant combatant: The combatant
        :param int x: The x position on the grid
        :param int y: The y position on the grid
        """
        position = self.grid.get_tile(x, y)
        if position is None:
            return
        position.add_occupation(combatant)
        combatant.X = x
        combatant.Y = y
        combatant.recalculate()
        self._combatants.append(combatant)

    def deal_damage(self, source, victim, damage):
        new_hp = victim.recieve_damage(damage)
        print("%s damages %s for %d damage, %d HP left" % (str(source), str(victim), damage, new_hp))
        if new_hp <= -10:
            print("%s is dead" % str(victim))
        elif new_hp < 0:
            print("%s is unconsciousness" % str(victim))

    # Move character to next tile
    def move_combatant(self, combatant, tile, provoke=True):
        # 1.
        prev_tile = self.tile_for_combatant(combatant)
        if prev_tile == tile:
            return

        print("moving %s from %s to %s" % (str(combatant), str(prev_tile), str(tile)))
        if prev_tile is not None:
            prev_tile.remove_occupation(combatant)

        combatant.X = tile.x
        combatant.Y = tile.y
        tile.add_occupation(combatant)
        # TODO: raise attacks of opportunity

    def next_round(self):
        """
        Ends the current round and starts a new round, resulting in new initiative rolls
        and reset action points.
        """
        print("Starting round %d" % self.round)
        for combatant in self._combatants:
            combatant.reset_round()

        for combatant in self._combatants:
            print(combatant, "'s turn")
            turn_state = combatant.get_turn_state()
            turn_state.on_round_start()
            complete = False
            action_generator = combatant.gen_actions(self, turn_state)
            # Hard limit on action generator
            iteration_limit = 20
            while not complete and iteration_limit > 0:
                try:
                    action = next(action_generator, turn_state)
                    if action is None:
                        pass
                    elif isinstance(action, BattleAction):
                        action.execute(self, turn_state)
                    # TODO: process interrupts?
                except StopIteration:
                    complete = True
                    break
                iteration_limit -= 1
            # Commit turn changes?
            turn_state.on_round_end()

        self.round += 1
        print("Round %d is complete" % self.round)

    # Return distance between tiles
    def distance_tiles(self, obj_a, obj_b):
        return math.sqrt((obj_a.X - obj_b.X) ** 2 + (obj_a.Y - obj_b.Y) ** 2)

    # Check if combatant obj_b is whithin reach of combatant obj_a
    def is_adjacent(self, obj_a, obj_b):
        return math.fabs(obj_a.X - obj_b.X) <= obj_a._reach and math.fabs(obj_a.Y - obj_b.Y) <= obj_a._reach

    # Check if object is enemy
    def is_enemy(self, char_a, char_b):
        if char_a == char_b:
            return False
        return True

    # Find best enemy
    def find_enemy(self, char):
        enemies = []
        for combatant in self._combatants:
            if self.is_enemy(char, combatant):
                enemies.append(combatant)

        if len(enemies) > 0:
            # TODO: find nearest
            return enemies[0]
        return None

    # Reroll initiative for all the objects
    def roll_initiative(self):
        print("Rolling new initiative order")
        for combatant in self._combatants:
            combatant.reset_round()
            initiative = combatant.current_initiative() + dice.d20.roll()
            print(combatant, "rolls %d for initiative" % initiative)
            self._combatants.update_priority(combatant, initiative)

    def tile(self, *args, **kwargs):
        """
        Returns the tile for a combatant or a position.

        possible arguments are:
        :param Combatant combatant: The combatant
        :param int x: Position x
        :param int y: Position y

        :rtype: Tile
        """
        combatant = kwargs.get("combatant", None)
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        if combatant is not None:
            return self.tile_for_combatant(combatant)
        if x is not None and y is not None:
            return self.tile_for_position(x, y)

    def tile_for_combatant(self, combatant):
        for tile in self.grid.get_tiles():
            if tile.has_occupation(combatant):
                return tile
        return None

    def tile_for_position(self, x, y):
        return self.grid.get_tile(x, y)

    def __repr__(self):
        max_x = 0
        max_y = 0
        for tile in self.grid.get_tiles():
            if tile.x > max_x:
                max_x = tile.x
            if tile.y > max_y:
                max_y = tile.y

        result = ""
        for y in range(1, max_y):
            for x in range(1, max_x):
                tile = self.grid.get_tile(x, y)
                tile_str = " "
                if len(tile._occupation) > 0:
                    tile_str = "X"
                result += " | " + str(tile_str)
            result += " |\n"
        return result

# Stat indexes
STAT_STR = 0
STAT_DEX = 1
STAT_CON = 2
STAT_INT = 3
STAT_WIS = 4
STAT_CHA = 5


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
        self._stats = [0,0,0,0,0,0]
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

    def set_stats(self, str, dex, con, int, wis, cha):
        self._stats = [str, dex, con, int, wis, cha]

    def get_attack(self):
        return self._BAB + self.strength_modifier()

    # Check if character is dead
    def is_dead(self):
        return self._health <= -10

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
        return core.ability_modifier(self.constitution())

    def charisma_mofifier(self):
        """
        returns the charisma modifier

        :rtype: int
        """
        return core.ability_modifier(self.charisma())

    def dexterity_mofifier(self):
        """
        returns the dexterity modifier

        :rtype: int
        """
        return core.ability_modifier(self.dexterity())

    def intellect_mofifier(self):
        """
        returns the intellect modifier

        :rtype: int
        """
        return core.ability_modifier(self.intellect())

    def strength_modifier(self):
        """
        returns the strength modifier

        :rtype: int
        """
        return core.ability_modifier(self.strength())

    def wisdom_mofifier(self):
        """
        returns the wisdom modifier

        :rtype: int
        """
        return core.ability_modifier(self.wisdom())

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


class BattleAction(object):
    """
    Models an action in a battle. This includes all actions that can
    possibly taken during a battle including, but not limited to:
    Moving, Attacking and using an Ability, Skill or Trait.
    """
    def __init__(self, combatant: Combatant):
        self._combatant = combatant

    # Get duration of the action
    def duration(self):
        return DURATION_STANDARD

    def can_execute(self, combatant):
        return False

    def execute(self, battle: Battle, state: TurnState):
        pass

    def text(self):
        return "generic action"

    # Returns action text for display
    def action_text(self):
        return "%s executes %s" % (self._combatant.get_name(), self.text())

