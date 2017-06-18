import math
import core
from grid import PriorityQueue, Tile, PathFinder
import dice

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
        self._combatants = PriorityQueue()
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
        self._combatants.append(combatant, combatant.current_initiative())

    # Move character to next tile
    def move(self, char, coord, provoke=True):
        # 1.
        pass

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
            for action in combatant.gen_actions(self):
                #action = combatant.next_action(self)
                if not action.can_execute(combatant):
                    continue

                action.execute()

        self.round += 1
        print("Round %d is complete" % self.round)

    def distance_tiles(self, obj_a, obj_b):
        return math.sqrt((obj_a.X - obj_b.X) ** 2 + (obj_a.Y - obj_b.Y) ** 2)


    def is_adjacent(self, obj_a, obj_b):
        return math.abs(obj_a.X - obj_b.X) <= obj_a.reach and math.abs(obj_a.Y - obj_b.Y) <= obj_a.reach

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
            return self.__tile_for_combatant(combatant)
        if x is not None and y is not None:
            return self.__tile_for_position(x, y)

    def __tile_for_combatant(self, combatant):
        for tile in self.grid.get_tiles():
            if tile.has_occupation(combatant):
                return tile
        return None

    def __tile_for_position(self, x, y):
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


# Contains current combatant characteristics
# Should be as flat as possible for better performance
class Combatant(object):
    """
    :type _is_flat_footed: bool
    :type _action_points: int
    :type _current_initiative: int
    """
    def __init__(self):
        self._is_flat_footed = False
        self._action_move = 0
        self._action_standard = 0
        self._action_full = 0
        self._action_5footstep = 0
        self._current_initiative = 0
        self.X = 0
        self.Y = 0

        self._stats = [0,0,0,0,0,0]
        self._experience = 0
        self._alignment = 0
        self._BAB = 0
        self._health_max = 0
        self._health = 0
        self._brain = None
        self._save_fort = 0
        self._save_ref = 0
        self._save_will = 0
        self._AC = 0
        self.move_speed = 30
        # Attack bonus for chosen maneuver/style
        self._attack_bonus_style = 0
        # Reach, in tiles
        self._reach = 1

    # Get armor class
    def get_AC(self):
        return 10 + self._AC + self.dex_bonus()

    def set_brain(self, brain):
        self._brain = brain
        brain.slave = self

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

    # Get available action list
    def gen_actions(self, battle):
        if self._brain is None:
            return []
        return self._brain.make_turn(battle)

    # Overriden by character
    def get_name(self):
        return "Unknown"


