import math
import core
from grid import Tile, PathFinder
import dice
import logging
from .combatant import Combatant, TurnState

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

    def add_combatant(self, combatant, x, y, **kwargs):
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
        combatant.set_faction(kwargs.get('faction', 'none'))
        combatant.X = x
        combatant.Y = y
        combatant.recalculate()
        self._combatants.append(combatant)

    def remove_combatant(self, combatant):
        """
        :param combatant: Combatant to be removed
        """
        tile = self.tile_for_combatant(combatant)
        if tile is None:
            pass
        self._combatants.remove(combatant)

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
        dead = []
        self.round += 1
        #print("Starting round %d" % self.round)
        for combatant in self._combatants:
            if combatant.is_dead():
                dead.append(combatant)
            combatant.reset_round()

        # Iterate all active combatants
        for combatant in self._combatants:
            if combatant.is_dead():
                dead.append(combatant)
            elif not combatant.is_consciousness():
                continue
            #print(combatant, "'s turn")
            turn_state = combatant.get_turn_state()
            turn_state.on_round_start()
            complete = False
            action_generator = combatant.gen_actions(self, turn_state)
            # Hard limit on action generator
            iteration_limit = 20
            while not complete and iteration_limit > 0:
                try:
                    action = next(action_generator)
                    if action is None:
                        pass
                    else: #action, BattleAction):
                        action.execute(self, turn_state)
                    # TODO: process interrupts?
                except StopIteration:
                    complete = True
                    break
                iteration_limit -= 1
            # Commit turn changes?
            turn_state.on_round_end()

        print("Round %d is complete" % self.round)

    # Return distance between tiles
    def distance_tiles(self, obj_a, obj_b):
        return math.sqrt((obj_a.X - obj_b.X) ** 2 + (obj_a.Y - obj_b.Y) ** 2)

    # Check if combatant obj_b is whithin reach of combatant obj_a
    def is_adjacent(self, obj_a, obj_b):
        reach = obj_a.total_reach()
        return math.fabs(obj_a.X - obj_b.X) <= reach and math.fabs(obj_a.Y - obj_b.Y) <= reach

    # Check if object is enemy
    def is_combatant_enemy(self, char_a, char_b):
        if char_a == char_b:
            return False
        return self.is_faction_enemy(char_a.get_faction(),char_b.get_faction())

    def is_faction_enemy(self, faction_a, faction_b):
        return faction_a != faction_b

    def path_to_range(self, src, target, range):
        start = self.tile_for_combatant(src)
        end = self.tile_for_combatant(target)
        path = self.pathfinder.path_to_range(start, end, range)
        return path

    # Find best enemy
    def find_enemy(self, char):
        enemies = []
        for combatant in self._combatants:
            if combatant.is_consciousness() and self.is_combatant_enemy(char, combatant):
                enemies.append(combatant)

        if len(enemies) > 0:
            # TODO: filter enemies by range
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

