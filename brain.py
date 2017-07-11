import math
import logging
from battle.actions import *
from battle.combatant import *


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

        print("Checking style %s. Score=%s" % (str(variation), str(score)))

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

    # Called when someone provokes attack of opportunity
    def respond_provocation(self, battle, target: Combatant, action=None):
        state = self.get_turn_state()
        if self.slave.opportunities_left() > 0 and state.attack_AoO is not None:
            print("%s uses opportunity to attack %s" % (self.slave.get_name(), target.get_name()))
            desc = self.slave.calculate_attack_of_opportunity(target)
            yield from self.slave.do_action_strike(desc)

    def get_turn_state(self) -> TurnState:
        return self.slave.get_turn_state()

    # Estimate fight probabilities against specified enemy
    def estimate_battle(self, enemy: Combatant):
        AC = enemy.get_armor_class()
        attacks = self.slave.generate_bab_chain(enemy)
        total_dmg = 0
        strikes = []
        for strike in attacks:
            dam, prob = strike.estimated_damage(self.slave, enemy)
            total_dmg += dam
            strikes.append("prob=%d;dam=%0.3f"%(prob,dam))
        print("Estimated strikes=[%s]. Round damage=%.2f" % (str(strikes), total_dmg))

    def find_enemy_target(self, battle, force = False):
        if self.target is None or force:
            self.target = battle.find_enemy(self.slave)
            if self.target is not None:
                print("%s found enemy: %s" % (self.slave.get_name(), str(self.target)))
                self.estimate_battle(self.target)
                return True
        return False


# Brain for simple movement and attacking
class MoveAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        self.logger = logging.getLogger("brain")

    def make_turn(self, battle):
        state = self.get_turn_state()


        if self.target is None:
            print("%s has no targets" % self.slave.get_name())
            return

        # 2. If enemy is in range - full round attack
        if self.slave.is_adjacent(self.target):
            self.logger.debug("target is near, can attack")
            while state.can_attack():
                if self.target.is_consciousness():
                    # Mark that we have used an action
                    desc = state.use_attack()
                    desc.update_target(self.target)
                    # TODO: update attack data according to selected target or custom attack
                    yield AttackAction(self.slave, desc)
                    #yield from battle.make_action_strike(self.slave, state, self.target, desc)
                else:
                    self.target = None
                    break
        elif state.can_move():
            self.logger.debug("farget %s is away. Finding path" % self.target.get_name())
            path = battle.path_to_melee_range(self.slave, self.target, self.slave.total_reach())
            self.logger.debug("found path of %d feet length" % path.length())
            yield from battle.make_action_move_tiles(self.slave, state, path)


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
            #yield WaitAction(self.slave)
            return

        # 2. If enemy is in range - full round attack
        if not self.slave.is_adjacent(self.target):
            self.logger.debug("target is far, can not attack")
            return

        self.logger.debug("target is near, can attack")
        while state.can_attack():
            if self.target.is_consciousness():
                # Mark that we have used an action
                desc = state.use_attack()
                desc.update_target(self.target)
                yield AttackAction(self.slave, desc)
            else:
                self.target = None
                break


# Object is controlled by keyboard input
class ManualBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        pass
