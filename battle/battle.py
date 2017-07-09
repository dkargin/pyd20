import types
from .dice import *
from battle.grid import Tile, Grid
from battle.pathfinder import PathFinder
from .combatant import Combatant, TurnState, AttackDesc

import battle.actions
import animation


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
        self.pathfinder = PathFinder(self.grid)
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
        combatant.on_round_start()
        self._combatants.append(combatant)
        self.grid.register_entity(combatant)
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

    def execute_combatant_action(self, action):
        """
        Executes minimal game action
        :param action:
        :return:
        """
        if action is None:
            return
        ret = action.execute(self)
        if isinstance(ret, types.GeneratorType):
            yield from action.execute(self)

    # Process turn for selected combatant
    def combatant_make_turn(self, combatant):
        # print(combatant, "'s turn")
        combatant.on_round_start()

        # Hard limit on action generator
        iteration_limit = 20

        # Iterate through all combatant actions during the turn
        for action in combatant.gen_brain_actions(self):
            yield from self.execute_combatant_action(action)

            iteration_limit -= 1
            if iteration_limit <= 0:
                break

        # Commit turn changes?
        combatant.on_round_end()

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
            print("Starting round %d" % self.round)
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
                yield from self.combatant_make_turn(combatant)

            yield None

        print(" ----==== Round %d is complete ====---- " % self.round)

    # Check if object is enemy
    def is_combatant_enemy(self, char_a, char_b):
        if char_a == char_b:
            return False
        return self.is_faction_enemy(char_a.get_faction(),char_b.get_faction())

    def is_faction_enemy(self, faction_a, faction_b):
        return faction_a != faction_b

    def path_to_melee_range(self, src, target, attack_range):
        start = self.tile_for_combatant(src)
        near = target.get_size()*0.5
        far = target.get_size()*0.5 + attack_range
        path = self.pathfinder.path_to_melee_range(start, target.get_center(), near, far)
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

    # Roll initiative for all the objects
    def roll_initiative(self):
        print("Rolling new initiative order")
        for combatant in self._combatants:
            combatant.reset_round()
            initiative = combatant.current_initiative() + d20.roll()
            print(combatant, "rolls %d for initiative" % initiative)
            self._combatants.update_priority(combatant, initiative)

    # TODO: Get rid of it
    def tile_for_combatant(self, combatant) -> Tile:
        return self.tile_for_position(combatant.x, combatant.y)

    def tile_for_position(self, x, y):
        return self.grid.get_tile(x, y)

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
            if self.tile_threatened(self.tile_for_position(tile.x + dx, tile.y + dy), combatant):
                return True
        return False

    ############## Action generators ################
    def make_action_move_tiles(self, combatant: Combatant, state: TurnState, path):
        # We should iterate all the tiles
        tiles_moved = []
        combatant.path = path

        # [0,1,2,3,4,5,6]
        # [0,0,0,T,T,0,0]
        # Moves: 0->3, 3->4, 4->6
        waypoints = path.get_path()
        while len(waypoints) > 0:
            tile = waypoints.pop(0)
            tiles_moved.append(tile)
            if self.position_threatened(combatant, tile.x, tile.y):
                yield battle.actions.MoveAction(combatant, tiles_moved)
                tiles_moved = []

            state.moves_left -= 5
            if state.moves_left <= 0:
                break

        # One last step
        if len(tiles_moved) > 0 is not None:
            yield battle.actions.MoveAction(combatant, tiles_moved)

        state.use_move()

    # Execute strike action
    def do_action_strike(self, combatant, desc: AttackDesc):
        yield animation.AttackStart(combatant, desc.get_target())
        attack, roll = desc.roll_attack()
        # Roll for critical confirmation
        crit_confirm, crit_confirm_roll = desc.roll_attack()
        target = desc.get_target()

        # TODO: run events for on_strike_begin(desc, target)
        armor_class = target.get_touch_armor_class(target) if desc.touch else target.get_armor_class(target)

        # TODO: run events for critical hit
        has_crit = desc.is_critical(roll) and (crit_confirm + desc.critical_confirm_bonus >= armor_class or crit_confirm_roll == 20)
        hit = attack >= armor_class
        if roll == 20:
            hit = True
        if roll == 1:
            hit = False

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

        print("%s %s %s with roll %d(%d+%d) vs AC=%d" %
              (combatant.get_name(), attack_text, target.get_name(), attack, roll, attack-roll, armor_class))
        if hit:
            target.receive_damage(damage, combatant)

        yield animation.AttackFinish(combatant, target)
        # TODO: run events for on_strike_finish()
