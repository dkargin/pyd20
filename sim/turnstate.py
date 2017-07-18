from .core import *
from .attackdesc import AttackDesc


# Encapsulates current turn state
class TurnState(object):
    def __init__(self):
        self.moves_left = 0
        self.move_actions = 2
        self.moved_distance = 0
        self.current_action = ACTION_TYPE_NONE
        self.standard_actions = 1
        # Considered that full-attack-action is started
        self.started_attacks = False
        self.moved_5ft = 0
        self.swift_actions = 1
        self.made_attack = 0
        # Available attacks
        self.attacks = []
        # Attack to be used for AoO
        self.attack_AoO = []

    def set_attacks(self, attacks):
        self.attacks = attacks

    # Use attack from generated attack list
    def use_attack(self) -> AttackDesc:
        """
        :return: AttackDesc
        """
        if len(self.attacks) > 0:
            attack = self.attacks.pop(0)
            self.made_attack += 1
            self.use_standard(attack=True)
            return attack
        self.started_attacks = True
        return None

    # Use move action
    def use_duration(self, duration):
        if duration == ACTION_TYPE_MOVE:
            self.move_actions -= 1
            self.move_5ft = 0
        elif duration == ACTION_TYPE_STANDARD:
            self.standard_actions -= 1

    # Returns true if character has attack actions
    def can_attack(self):
        # Should return true if made standard attack and going to continue full round attack
        # Should return false if both standard action and move action are expended
        # Move action should be expended after making a second attack
        # Third (and more) attacks should be available after a second attack
        return len(self.attacks) > 0 and (self.standard_actions > 0 or self.started_attacks > 0)

    # If can take any sort of move actions
    def can_move(self):
        return self.move_actions > 0 or self.standard_actions > 0

    # Can make 'move' actions that actually move combatant
    def can_move_distance(self):
        return self.move_actions > 0 and self.moved_5ft == 0

    def can_5ft_step(self):
        return self.moved_5ft == 0 and self.moved_distance == 0

    # Use standard action
    def use_standard(self, attack=False):
        if not attack and self.standard_actions > 0:
            self.made_attack = 1
            self.move_actions -= 1
            self.standard_actions -= 1
        elif attack and self.made_attack > 0:
            self.move_actions = 0
        self.standard_actions = 0

    # Use full round action
    def use_full_round(self):
        if self.standard_actions > 0 and self.move_actions > 0:
            self.standard_actions -= 1
            self.move_actions -= 1
            return True
        return False

    def complete(self):
        return not self.can_attack() and not self.can_move()
