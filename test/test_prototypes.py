from unittest import TestCase
import dice


class Action:
    def __init__(self, name, fail=False):
        self.name = name
        self.fail = fail

    def execute(self):
        if self.fail:
            print("Failed to execute action %s" % self.name)
        else:
            print("Executed action %s" % self.name)
        return not self.fail


class ActionInterrupted(BaseException):
    def __init__(self, action, result):
        BaseException.__init__(self)
        self.action = action
        self.result = result

# Does moving action
def action_move(distance):
    yield Action("move", True if distance == 4 else False)

# Creates 'attack' action
def action_attack():
    yield Action("attack")

def charge_attack(distance):
    reached = True
    while distance > 0:
        try:
            result = yield from action_move(distance)
        except ActionInterrupted as e:
            print("-interrupted")
            reached = False
            # If you return right here, than 'for ... in generator' traversal breaks with 'StopIteration'
            raise
        distance -= 1
    if reached:
        yield from action_attack()
    else:
        yield Action("dumbfaced")

# Mimics AI action generator
def dummy_ai_generator(distance):
    yield Action("wield axe")
    try:
        yield from charge_attack(distance)
    except ActionInterrupted as e:
        print("charge_attack was interrupted")

def traverse_action_generator(gen):
    iterations = 20
    for action in gen:
        result = action.execute()
        if not result:
            try:
                gen.throw(ActionInterrupted(action, result))
            # For the case when generator has no yield after interrupt handler
            except StopIteration: pass
    """
    try:
        action = next(gen)
        while iterations > 0:
            if action is not None:
                result = action.execute()
            action = gen.send(result)
            iterations -= 1
    except StopIteration:
        pass
    except:
        raise
    """



class DiceTest(TestCase):
    def test_dice(self):
        dice1 = dice.Dice("2d6")
        print("Dice1=%s"%dice1.to_string())
        dice2 = dice.Dice("3d6")
        print("Dice2=%s"%dice2.to_string())
        dice3 = dice.Dice("1d8")
        print("Dice3=%s"%dice3.to_string())

        dice_sum1 = dice1+dice2
        print("sum1=%s"%dice_sum1.to_string())
        dice_sum2 = dice_sum1 + dice3
        print("sum2=%s"%dice_sum2.to_string())

        assert(True)

    def test_nested_actions(self):
        print("\ntest with normal flow")
        traverse_action_generator(dummy_ai_generator(3))

        print("\ntest with interrupted flow")
        traverse_action_generator(dummy_ai_generator(6))

        assert (True)

