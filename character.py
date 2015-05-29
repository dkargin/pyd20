#!/usr/bin/python3
# -*- coding: utf-8 -*-
import dice
import core


class Character(object):

    """
    implements a character
    """

    def __init__(self):
        self._constitution = 0
        self._charisma = 0
        self._dexterity = 0
        self._intellect = 0
        self._strength = 0
        self._wisdom = 0
        self._name = None
        self._alignment = [None, None]
        self._class = None

    def set_class(self, class_type):
        self._class = class_type


class Class(object):

    """
    implements a class
    """

    def __init__(self):
        self._hit_die = None
        self._attack_bonus_type = None
        self._will_save_bonus_type = None
        self._fortitude_save_bonus_type = None
        self._reflex_save_bonus_type = None
        self._skill_modifier = None
        self._possible_alignments = list()
        self._class_skills = list()
        self._special = list()

    def attack_bonus(self, level):
        return core.attack_bonus(level, self._attack_bonus_type)

    def will_save_bonus(self, level):
        return core.save_bonus(level, self._will_save_bonus_type)

    def fortitude_save_bonus(self, level):
        return core.save_bonus(level, self._fortitude_save_bonus_type)

    def reflex_save_bonus(self, level):
        return core.save_bonus(level, self._reflex_save_bonus_type)

    def roll_hit_die(self):
        return self._hit_die.roll()

    def skill_points(self, int_modifier):
        if int_modifier < 0:
            int_modifier = 0
        return (self._skill_modifier + int_modifier)
