import math
import logging
from sim.actions import *
from sim.combatant import *


# Estimate fight probabilities against specified enemy
def estimate_attack_round(attacker: Combatant, defender: Combatant):
    attacks = attacker.generate_bab_chain(defender)
    total_dmg = 0
    for strike in attacks:
        dam, prob = strike.estimated_damage(attacker, defender)
        strike.prob = 100*prob
        total_dmg += dam
    return attacks, total_dmg


class StrikeExchange:
    def __init__(self, a: Combatant, b: Combatant, data):
        attacks_a, dmg_a = estimate_attack_round(a, b)
        self.a = a
        self.attacks_a = attacks_a
        self.dmg_a = dmg_a
        self.rounds_a = b.health / dmg_a if dmg_a > 0 else 1000

        attacks_b, dmg_b = estimate_attack_round(b, a)
        self.b = b
        self.attacks_b = attacks_b
        self.dmg_b = dmg_b
        self.rounds_b = a.health / dmg_b if dmg_b > 0 else 1000

        self.data = data

    def delta(self):
        return self.dmg_a - self.dmg_b

    # Make score for exchange
    def score(self):
        if self.rounds_a < self.rounds_b:
            return self.rounds_a * self.dmg_b, True
        else:
            return self.rounds_b * self.dmg_a, False

    def seq_str(self, seqence):
        text = ""
        for strike in seqence:
            text += "\n\t%s" % str(strike)
        return text

    def __str__(self):
        seq_a = self.seq_str(self.attacks_a)
        seq_b = self.seq_str(self.attacks_b)
        text = ""
        text += "A strikes vs AC=%d: %s" % (self.b.get_armor_class(self.a), seq_a)
        text += "\nB strikes vs AC=%d: %s" % (self.a.get_armor_class(self.b), seq_b)
        return text


# Estimating battle between combatant 'a' and 'b'
def estimate_battle(a: Combatant, b: Combatant):
    # Estimate attack a to b
    attacks_a, dmg_a = estimate_attack_round(a, b)
    rounds_a = b.health / dmg_a if dmg_a > 0 else 1000
    # Estimate attack b to a
    attacks_b, dmg_b = estimate_attack_round(b, a)
    rounds_b = a.health / dmg_b if dmg_b > 0 else 1000

    return dmg_a - dmg_b, min(rounds_a, rounds_b), attacks_a, attacks_b


class StyleSet:
    def __init__(self, styles):
        self.styles = styles

    def activate(self, combatant: Combatant):
        for style in self.styles:
            combatant.activate_style(style)

    def deactivate(self, combatant: Combatant):
        for style in self.styles:
            combatant.deactivate_style(style)

    def __str__(self):
        return str(self.styles)


def pick_by_bitmask(data, bitmask, max):
    result = []
    for i in range(0, max):
        if bitmask & (1 << i):
            result.append(data[i])
    return result


# Generate style variations
def style_variations(a: Combatant):
    style_list = list(a._known_styles)
    max_choice = 1 << len(style_list)

    for mask in range(0, max_choice):
        styles = pick_by_bitmask(style_list, mask, len(style_list))
        yield StyleSet(styles)


def find_best_style(a: Combatant, b: Combatant):
    best_style = None
    best_exchange = None
    best_score = 0
    for variation in style_variations(a):

        variation.activate(a)
        exchange = StrikeExchange(a,b, variation)
        score = exchange.score()

        print("Checking style %s. Score=%s, survive=%s" % (str(variation), str(score[0]), str(score[1])))

        variation.deactivate(a)
        if best_style is None or score > best_score:
            best_style = variation
            best_exchange = exchange
            best_score = score

    return best_style, best_exchange, best_score


class Brain(object):
    """
    Base class for combatant AI
    :type slave: Combatant | None
    :type target: Combatant | None
    """
    def __init__(self):
        self.slave = None
        # Attack target
        self.target = None
        # Path to follow
        self.path = None
        self.logger = logging.getLogger("brain")
        self._allow_move = True
        self._allow_attack = True
        self._allow_spells = True

    # Prepare to start a turn
    # Used for selecting fighting styles, activating feats and so on
    def prepare_turn(self, battle):
        # Trying iteratively use all turn actions
        if self.find_enemy_target(battle):
            style, exchange, score = find_best_style(self.slave, self.target)
            print("Best style %s provides %s damage" % (str(style), str(score)))
            print(str(exchange))

    # Brain make its turn right here
    def make_turn(self, battle):
        pass

    # Return a list of available actions for current state
    def what_can_i_do(self, battle: Battle, state: TurnState, **kwargs):
        """
        Returns a dict that maps DURATION -> list of actions to do in current turn state

        Move:
         - move to target
         - move to safety
         - move to any point in area (who needs it except manual player?)
        Attack:
         - attack a target
         - custom attack target
         ...
        Activate a style
        Custom actions:
         - activate effect
        """
        result = {}

        def add_result(act):
            duration = act.duration
            if duration not in result:
                result[duration] = []
            result[duration].append(act)

        # Add relevant attack actions. Iterate through
        # Add custom actions
        for name, action in self._combatant._custom_actions.items():
            add_result(action)

        return result

    # Called when someone provokes attack of opportunity
    def respond_provocation(self, battle, target: Combatant, action=None):
        state = self.get_turn_state()
        if self.slave.opportunities_left() > 0 and state.attack_AoO is not None:
            print("%s uses opportunity to attack %s" % (self.slave.get_name(), target.get_name()))
            desc = self.slave.calculate_attack_of_opportunity(target)
            yield from self.slave.do_action_strike(battle, desc)

    def get_turn_state(self) -> TurnState:
        return self.slave.get_turn_state()

    # Estimate fight probabilities against specified enemy
    def estimate_battle(self, enemy: Combatant):
        attacks = self.slave.generate_bab_chain(enemy)
        total_dmg = 0
        strikes = []
        for strike in attacks:
            dam, prob = strike.estimated_damage(self.slave, enemy)
            total_dmg += dam
            strikes.append("prob=%d;dam=%0.3f"%(100*prob,dam))
        print("Estimated strikes=[%s]. Round damage=%.2f" % (str(strikes), total_dmg))

    def find_enemy_target(self, battle, force = False):
        if self.target is None or force:
            self.target = battle.find_enemy(self.slave)
            if self.target is not None:
                print("%s found enemy: %s" % (self.slave.get_name(), str(self.target)))
                self.estimate_battle(self.target)
                return True
        return False

    def can_attack(self, target):
        weapon = self.slave.get_main_weapon()
        if weapon.is_ranged():
            max_range = weapon.range()
            center = self.slave.get_center()
            distance = center.distance(target.get_center())
            return max_range >= distance
        else:
            return self.slave.is_adjacent(target)

    def in_charge_range(self, target:Entity):
        if self.slave.has_status_flag(STATUS_FLAG_EXHAUSTED):
            return False
        distance_to_target = self.slave.distance_melee(target)*5
        # 1. Check if target is within double move range
        if distance_to_target > self.slave.move_speed*2:
            return False
        return True

    def can_trip(self, target):
        slave = self.slave
        if not target.has_status_flag(STATUS_PRONE):
            return False
        # There are some ways to make ranged trip
        return slave.get_main_weapon().can_trip() or slave.has_status_flag(STATUS_HAS_IMPROVED_TRIP)


# Brain for simple movement and attacking
class MoveAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)

    def make_turn(self, battle):
        state = self.get_turn_state()

        if self.target is None:
            print("%s has no targets" % self.slave.get_name())
            return

        no_charge = False

        while not state.complete():
            if self.slave.has_status_flag(STATUS_PRONE):
                yield StandUpAction(self.slave)

            need_move = False

            # Use all the attacks
            if self.target.is_consciousness():
                if self.in_charge_range(self.target) and not no_charge:
                    # Pick best tile for charging
                    path = battle.pathfinder.check_straight_path(self.slave.get_coord(), self.target.get_coord())
                    if path is not None:
                        yield from self.slave.do_action_charge(battle, state, self.target, path)
                        continue
                    else:
                        no_charge = True
                # 2. If enemy is in range - full round attack
                elif self.can_attack(self.target):
                    self.logger.debug("target is near, can attack")

                    if self.can_trip(self.target):
                        yield TripAttackAction(self.slave, self.target)
                    else:
                        yield AttackAction(self.slave, self.target)
                else:
                    need_move = True
            else:
                self.target = None
                break

            if state.can_move_distance() and self.target is not None and need_move:
                self.logger.debug("target %s is away. Finding path" % self.target.name)
                path = battle.path_to_melee_range(self.slave, self.target, self.slave.total_reach())
                self.logger.debug("found path of %d feet length" % path.length())
                yield from self.slave.do_action_move_tiles(battle, state, path)

        self.logger.debug("%s has done thinking" % self.slave.name)


# Brain that attacks only if enemy is adjacent
class StandAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        self.logger = logging.getLogger("brain")

    def make_turn(self, battle):
        state = self.get_turn_state()
        # Trying iteratively use all turn actions
        # 1. If no enemy - find it
        self.find_enemy_target(battle)

        if self.target is None:
            print("%s has no targets" % self.slave.get_name())
            return

        if self.slave.has_status_flag(STATUS_PRONE):
            yield StandUpAction(self.slave)

        # 2. If enemy is in range - full round attack
        if not self.slave.is_adjacent(self.target):
            self.logger.debug("target is far, can not attack")
            return

        self.logger.debug("target is near, can attack")
        while state.can_attack():
            if self.target.is_consciousness():
                yield AttackAction(self.slave, self.target)
            else:
                self.target = None
                break


# Object is controlled by keyboard input
class ManualBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        pass
