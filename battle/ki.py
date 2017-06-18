from .actions import *
from character import Character


class KiCharacter(Character):

    def __can_attack(self, battle):
        return False

    def __move_to_next_enemy(self, battle):
        current_tile = battle.tile(combatant=self)
        enemy_tiles = list()
        for tile in battle.grid.get_tiles():
            if not tile.is_empty() and not tile.has_occupation(self):
                enemy_tiles.append(tile)
        if len(enemy_tiles) is 0:
            return EndTurnAction()
        closest_enemy = None
        shortest_distance = 999
        for enemy_tile in enemy_tiles:
            # calculating euclidean distance
            dx = abs(current_tile.x - enemy_tile.x)
            dy = abs(current_tile.y - enemy_tile.y)
            d_euclidean = dx + dy
            if d_euclidean < shortest_distance or closest_enemy is None:
                closest_enemy = enemy_tile
                shortest_distance = d_euclidean
        shortest_move_tile = None
        shortest_distance = 999
        for adjacent_tile in battle.grid.get_adjacent_tiles(closest_enemy):
            # calculating euclidean distance
            dx = abs(current_tile.x - adjacent_tile.x)
            dy = abs(current_tile.y - adjacent_tile.y)
            d_euclidean = dx + dy
            if d_euclidean < shortest_distance or shortest_move_tile is None:
                shortest_move_tile = adjacent_tile
                shortest_distance = d_euclidean
        if shortest_move_tile.has_occupation(self):
            return EndTurnAction()
        return MoveAction(self, battle.grid.path_between_tiles(current_tile, shortest_move_tile))

    def __attack_next_enemy(self, battle):
        return EndTurnAction()

    def next_action(self, battle):
        if self._action_points == 0:
            return EndTurnAction()
        if not self.__can_attack(battle):
            return self.__move_to_next_enemy(battle)
        return self.__attack_next_enemy(battle)
