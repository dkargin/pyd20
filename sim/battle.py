import types
from .dice import *
from .core import *
from sim.grid import Tile, Grid
from sim.pathfinder import PathFinder
from .combatant import Combatant, AttackDesc
from .turnstate import TurnState

import sim.actions
import sim.events as events


class Battle(object):
    NEXT_ACTION = 1
    """
    Models a battle

    :type grid: grid.Grid
    :type _combatants: Combatant[]
    :type round: int - Current round
    """
    def __init__(self, grid_width, grid_height):
        """
        Creates an instance of a battle.
        """
        self._grid = Grid(grid_width, grid_height)
        #self.pathfinder = PathFinder(self.grid)
        self._combatants = []
        self.round = 0

    @property
    def grid(self):
        return self._grid

    @property
    def combatants(self):
        return self._combatants

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

        combatant.set_faction(kwargs.get('faction', 'none'))
        combatant.x = x
        combatant.y = y
        combatant.recalculate()
        self._combatants.append(combatant)
        self.grid.register_entity(combatant)
        combatant.on_attach_to_grid(self.grid)
        combatant.on_turn_start(self, False)

        combatant.fix_visual()

    def remove_combatant(self, combatant):
        """
        :param combatant: Combatant to be removed
        """
        self._combatants.remove(combatant)
        self.grid.unregister_entity(combatant)

    def print_characters(self):
        for ch in self._combatants:
            print(ch.print_character())

    # Gather attacks of opportunity, provoked by combatant, standing at specified tile
    def get_threatening_enemies(self, combatant: Combatant, action):
        opportunity_attacks = []
        is_enemy = lambda a: self.is_combatant_enemy(a, combatant) and combatant.opportunities_left() > 0

        for tile in combatant.tiles_threatened_by_enemies():
            for attacker in filter(is_enemy, tile.threaten):
                opportunity_attacks.append(attacker)
        return opportunity_attacks

    def execute_combatant_action(self, action, state):
        """
        Executes minimal game action
        :param action:
        :return:
        """
        if action is None:
            return
        ret = action.execute(self, state)
        if isinstance(ret, types.GeneratorType):
            yield from action.execute(self, state)

    # Process turn for selected combatant
    def combatant_make_turn(self, combatant):
        # print(combatant, "'s turn")
        state = combatant.on_turn_start(self)

        # Hard limit on action generator
        iteration_limit = 20

        # Iterate through all combatant actions during the turn
        for action in combatant.gen_brain_actions(self):
            yield from self.execute_combatant_action(action, state)

            iteration_limit -= 1
            if iteration_limit <= 0:
                break

        # Commit turn changes?
        combatant.on_turn_end()
        yield events.TurnEnd(combatant)

    def battle_generator(self):
        """
        Endless 'thread-like' function tnat runs battle processing
        Each 'yield' returns an animation, that main game loop should show
        until next game action can be issued

        yield Animation - stop turn processing and render animation, until it is complete
        yield ...
        """
        while True:
            dead = []
            self.round += 1
            print("======================================\nStarting round %d" % self.round)
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
                else:
                    yield from self.combatant_make_turn(combatant)

            yield events.RoundEnd(self.round)


        print(" ----==== Round %d is complete ====---- " % self.round)

    # Check if object is enemy
    def is_combatant_enemy(self, char_a, char_b):
        if char_a == char_b:
            return False
        return self.is_faction_enemy(char_a.get_faction(),char_b.get_faction())

    def is_faction_enemy(self, faction_a, faction_b):
        return faction_a != faction_b

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

    # Roll initiative for all the objects
    def roll_initiative(self):
        print("Rolling new initiative order")
        for combatant in self._combatants:
            combatant.reset_round()
            initiative = combatant.current_initiative() + d20.roll()
            print(combatant, "rolls %d for initiative" % initiative)
            self._combatants.update_priority(combatant, initiative)

    # TODO: Get rid of it
    #def tile_for_combatant(self, combatant) -> Tile:
    #    return self.tile_for_position(combatant.x, combatant.y)

    #def tile_for_position(self, x, y):
    #    return self.grid.get_tile(x, y)

    def tile_threatened(self, tile, combatant):
        if tile is None:
            return False
        for u in tile.threaten:
            if self.is_combatant_enemy(u, combatant):
                return True
        return False

    def position_threatened(self, combatant, x, y):
        dx = x - combatant.x
        dy = y - combatant.y
        for tile in combatant.occupied_tiles:
            tile = self._grid.get_tile(tile.x + dx, tile.y + dy)
            if self.tile_threatened(tile, combatant):
                return True
        return False

    ############## Action generators ################
    def provoke_opportunity(self, combatant, action, exclude=[]):
        enemies = self.get_threatening_enemies(combatant, action)
        for enemy in enemies:
            if enemy not in exclude:
                yield from enemy.respond_provocation(self, combatant, action)


