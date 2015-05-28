#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random


class Die(object):

    """
    implements a die
    """

    def __init__(self, sides):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)


class Dice(object):

    """
    implements multiple dice
    """

    def __init__(self):
        self.dice = list()

    @staticmethod
    def from_string(string):
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
            instance.add_die(Die(sides))
        return instance

    def add_die(self, die):
        self.dice.append(die)

    def remove_die(self, die):
        self.dice.remove(die)

    def roll(self):
        roll_sum = 0
        for die in self.dice:
            roll_sum += die.roll()
        return roll_sum


def roll(dice_sting):
    if "+" in dice_sting:
        parts = dice_sting.replace(" ", "").split("+")
        return Dice.from_string(parts[0]).roll() + int(parts[1])
    if "-" in dice_sting:
        parts = dice_sting.replace(" ", "").split("-")
        return Dice.from_string(parts[0]).roll() - int(parts[1])
    return Dice.from_string(dice_sting).roll()

d4 = Die(4)
d6 = Die(6)
d8 = Die(8)
d10 = Die(10)
d20 = Die(20)
d100 = Die(100)
