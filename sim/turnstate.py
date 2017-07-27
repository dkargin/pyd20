from .core import *
from .attackdesc import AttackDesc


"""
Standard action can be spend as a move action
There are feats:
- that allow more move or standard actions per turn
- that allow double full round attack
- custom full round action that consists of attack chain (ToB has a lot of this stuff)
"""


# Encapsulates current turn state
class TurnState(object):

    STATE_INITIAL = 0
    # made one attack. If we make another attack - we spend std+move actions and switch to STATE_FULL_ROUND_ATTACK
    # if we make a move action (larger than 5ft), then std action is expended
    STATE_BEGAN_ATTACK = 1
    # Making full round attack. Move+Std is already spent, but we can continue our attack chain
    STATE_FULL_ROUND_ATTACK = 2
    # Done standard action after start of the a turn.
    STATE_DONE_STANDARD = 3
    # Began move action. Can iteratively make move distance actions up to movement limit
    STATE_BEGAN_MOVEMENT = 4
    # Turn is complete, nothing to do here
    STATE_COMPLETE = 5
    # Move as part of charge attack
    STATE_CHARGE_MOVE = 6

    def __init__(self):
        self._moves_left = 0
        self.move_actions = 1
        self._moved_distance = 0
        self.standard_actions = 1
        self.moved_5ft = 0
        self.swift_actions = 1
        self._state = TurnState.STATE_INITIAL
        # Available attacks
        self.attacks = []
        # Attack to be used for AoO
        self.attack_AoO = []

    @property
    def moves_left(self):
        return self._moves_left

    @property
    def moved_total(self):
        return self._moved_distance

    # Refresh internal data for turn start
    # This values can be modified during character event 'on_start_turn'
    def start_turn(self, combatant):
        self._moves_left = combatant.move_speed
        self.move_actions = 1
        self._moved_distance = 0
        self.standard_actions = 1
        self.moved_5ft = 0
        self.swift_actions = 1
        self._state = TurnState.STATE_INITIAL

    @property
    def state(self):
        return self._state

    def set_attacks(self, attacks):
        self.attacks = attacks

    # Use attack from generated attack list
    def next_attack(self, combatant) -> AttackDesc:
        """
        :return: AttackDesc
        """
        if len(self.attacks) > 0:
            attack = self.attacks.pop(0)
            self.use_action(combatant, ACTION_TYPE_ATTACK)
            return attack
        return None

    # Returns true if character has attack actions
    def can_attack(self):
        # Should return true if made standard attack and going to continue full round attack
        # Should return false if both standard action and move action are expended
        # Move action should be expended after making a second attack
        # Third (and more) attacks should be available after a second attack
        if self._state == TurnState.STATE_INITIAL:
            return len(self.attacks) > 0 and self.standard_actions > 0
        elif self._state in (TurnState.STATE_BEGAN_ATTACK, TurnState.STATE_FULL_ROUND_ATTACK):
            return len(self.attacks) > 0
        else:
            return len(self.attacks) > 0 and self.standard_actions > 0

    # If can take any sort of move actions
    def can_move(self):
        if self._state in (TurnState.STATE_INITIAL, TurnState.STATE_BEGAN_MOVEMENT, TurnState.STATE_DONE_STANDARD):
            return self.move_actions > 0 or self.standard_actions > 0
        return False

    # Can make 'move' actions that actually move combatant
    def can_move_distance(self):
        if self._state == TurnState.STATE_INITIAL:
            return self.move_actions > 0 or self.standard_actions > 0
        elif self._state == TurnState.STATE_BEGAN_MOVEMENT:
            return self.moves_left > 0
        return False

    def can_5ft_step(self):
        return self.moved_5ft == 0 and self._moved_distance == 0

    def use_action(self, combatant, action_type, **kwargs):
        """
        Finite state machine for making a turn.
        All actions should call it after being executed
        :param combatant:Combatant combatant that takes an action
        :param action:int action type, as defined in core.py
        :return:bool Whether action is executed properly
        """
        # print("%s is using action=%d, state=%s" % (combatant.name, action_type, TurnState.state_name(self._state)))
        while True:
            if self._state == TurnState.STATE_INITIAL:
                if action_type == ACTION_TYPE_ATTACK:
                    if self.standard_actions > 0:
                        self.standard_actions -= 1
                        # If also have move action, then can start full attack sequence
                        if self.move_actions > 0:
                            self._state = TurnState.STATE_BEGAN_ATTACK
                        return True
                    return False
                elif action_type == ACTION_TYPE_STANDARD:
                    if self.standard_actions > 0:
                        self.standard_actions -= 1
                        return True
                elif action_type == ACTION_TYPE_MOVE_LIKE:
                    # Expend move or standard action. Transition to the same state
                    if self.move_actions > 0:
                        self.move_actions -= 1
                    elif self.standard_actions > 0:
                        self.standard_actions -= 1
                    else:
                        raise ValueError("All actions are expended")
                    return True
                elif action_type == ACTION_TYPE_MOVE:
                    if self.move_actions > 0:
                        self.move_actions -= 1
                    elif self.standard_actions > 0:
                        self.standard_actions -= 1
                    else:
                        raise ValueError("All actions are expended")
                    # Regenerate current move actions
                    self._moves_left = combatant.move_speed
                    distance = kwargs.get('distance', 0)
                    if distance < self._moves_left:
                        self._state = TurnState.STATE_BEGAN_MOVEMENT
                        self._moves_left -= distance
                        self._moved_distance += distance
                    elif distance == self._moves_left:
                        self._moved_distance += distance
                    elif distance > self._moves_left:
                        raise ValueError("Trying to move too far")
                    return True
                return False
            elif self._state == TurnState.STATE_BEGAN_ATTACK:
                if action_type == ACTION_TYPE_ATTACK:
                    self._state = TurnState.STATE_FULL_ROUND_ATTACK
                    if self.move_actions > 0:
                        self.move_actions -= 1
                    else:
                        raise ValueError('Have no move actions to start an attack')
                    return True
                elif action_type == ACTION_TYPE_MOVE:
                    # Previous attack is considered a standard action
                    self.standard_actions -= 1
                    self._state = TurnState.STATE_BEGAN_MOVEMENT
                elif action_type == ACTION_TYPE_MOVE_LIKE:
                    self._state = TurnState.STATE_INITIAL
                    # Previous attack is considered a standard action
                    self.standard_actions -= 1
                    self.move_actions -= 1
                # All other actions are invalid
                return False
            elif self._state == TurnState.STATE_BEGAN_MOVEMENT:
                if action_type == ACTION_TYPE_MOVE:
                    # Can continue movement until move speed is exhausted
                    distance = kwargs.get('distance', 0)
                    if distance <= self.moves_left:
                        self._moved_distance += distance
                        self._moves_left -= distance
                        if self.moves_left == 0:
                            self._moves_left = combatant.move_speed
                            self._state = TurnState.STATE_INITIAL
                        return True
                    else:
                        return False
                else: # Any other action resets 'in movement' state to 'initial'
                    self._state = TurnState.STATE_INITIAL
                    # Need to regenerate move speed, because it can be used later from 'initial' state
                    self._moves_left = combatant.move_speed
                    continue

            return False
        return False

    def __str__(self):
        result = "state=%s, std=%d, move=%d, traveled=%dft, can_travel=%dft" % (
            TurnState.state_name(self._state),
            self.standard_actions, self.move_actions,
            self._moved_distance, self.moves_left,
        )
        return result

    # Use full round action
    def use_full_round(self):
        if self.standard_actions > 0 and self.move_actions > 0:
            self.standard_actions -= 1
            self.move_actions -= 1
            return True
        return False

    def complete(self):
        return not self.can_attack() and not self.can_move()

    @staticmethod
    def state_name(state):
        """
        :param state:int Turn state
        :return:string String that represents current internal state
        """
        if state == TurnState.STATE_INITIAL:
            return 'initial'
        elif state == TurnState.STATE_BEGAN_ATTACK:
            return 'began_attack'
        elif state == TurnState.STATE_BEGAN_MOVEMENT:
            return 'began_movement'
        elif state == TurnState.STATE_FULL_ROUND_ATTACK:
            return 'full_round_attack'
        elif state == TurnState.STATE_DONE_STANDARD:
            return 'done_standard_action'
        elif state == TurnState.STATE_COMPLETE:
            return 'complete'
        raise ValueError('Invalid TURN_STATE %d' % state)
