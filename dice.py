import random


class Dice(object):

    """
    implements multiple dice

    :type dice: Die[]
    """

    def __init__(self, string=None):
        """
        Creates a Dice object. It models multiple Die objects.
        """
        # Positive dice set
        self.dice = {}

        if string is not None:
            parts = string.lower().split("d")
            if len(parts) != 2:
                return
            if parts[0] == '':
                amount = 1
            else:
                amount = int(parts[0])
            sides = int(parts[1])
            self.add_die(sides, amount)

    def copy(self):
        result = Dice()
        result.dice = self.dice.copy()
        return result

    @staticmethod
    def from_string(string):
        """
        create dice from a string in the form:
        <amount>d<sides>
        for example:
        '3d6' creates a group with 3 six-sided dice

        :rtype: Dice
        """
        instance = Dice()
        parts = string.lower().split("d")
        if len(parts) != 2:
            return instance
        if parts[0] == '':
            amount = 1
        else:
            amount = int(parts[0])
        sides = int(parts[1])
        for i in range(amount):
            instance.add_die(sides)
        return instance

    @staticmethod
    def roll_dice(sides, count=1):
        """
        roll the die
        """
        result = 0
        for i in range(0, count):
            result += random.randint(1, sides) if sides > 1 else 1
        return result

    def add_die(self, side, count = 1):
        """
        add a die to the dice group
        """
        if side in self.dice:
            self.dice[side] += count
        else:
            self.dice[side] = count

    def remove_die(self, die):
        """
        remove a die from the dice group
        """
        self.dice.remove(die)

    def __add__(self, other):
        result = self.copy()
        for side, count in other.dice.items():
            result.add_die(side, count)
        return result

    # Get dice range, [min, max]
    def get_range(self):
        min = 0
        max = 0
        for side, count in self.dice.items():
            min += count
            max += side*count
        return min, max

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        result = ""
        first = True
        for side, count in self.dice.items():
            str = "%d" % (count) if side == 1 else "%dd%d" % (count, side)
            if count > 0:
                if first:
                    result += str
                    first = False
                else:
                    result += "+" + str
            elif count < 0:
                result += "-" + str
        return result

    # Remove zero-count dices
    def trim_zero(self):
        zeros = []
        # Collecting zeros
        for side, count in self.dice:
            if count == 0:
                zeros.append(side)
        # Removing zeros
        for side in zeros:
            del self.dice[side]

    def roll(self):
        """
        roll the dice group
        :rtype: int
        """
        roll_sum = 0
        for side, count in self.dice.items():
            roll_sum += Dice.roll_dice(side, count)

        return roll_sum


def roll(dice_sting):
    """
    rolls dice that are represented by a string in the form:
    <amount>d<sides>[<+/-><value>]
    for example:
    '3d6' rolls a group with 3 six-sided dice
    '2d10+5' rolls two ten sided die and adds 5 to the result

    :rtype: int result of the roll
    """
    if "+" in dice_sting:
        parts = dice_sting.replace(" ", "").split("+")
        return Dice.from_string(parts[0]).roll() + int(parts[1])
    if "-" in dice_sting:
        parts = dice_sting.replace(" ", "").split("-")
        return Dice.from_string(parts[0]).roll() - int(parts[1])
    return Dice.from_string(dice_sting).roll()

d4 = Dice("d4")
d6 = Dice("d6")
d8 = Dice("d8")
d10 = Dice("d10")
d20 = Dice("d20")
d100 = Dice("d100")

