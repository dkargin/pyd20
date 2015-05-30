#!/usr/bin/python3
# -*- coding: utf-8 -*-
import core
import json
from dice import Dice


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
    CLASS_DATA = "data/clsses.json"

    def __init__(self):
        self._hit_die = None
        self._attack_bonus_type = None
        self._will_save_bonus_type = None
        self._fortitude_save_bonus_type = None
        self._reflex_save_bonus_type = None
        self._skill_modifier = None
        self._name = None
        self._possible_alignments = list()
        self._class_skills = list()
        self._class_feats = list()
        self._ex_feats = list()
        self._special = list()

    @staticmethod
    def load(class_name):
        classes = json.loads(open(Class.CLASS_DATA).read())
        class_data = None
        for c in classes:
            if c["class_name"].lower() == class_name.lower():
                class_data = c
                break
        instance = Class()
        instance._name = class_data["class_data"]
        instance._hit_die = Dice.from_string(class_data["hit_die"])
        instance._attack_bonus_type = class_data["attack_bonus_type"]
        instance._skill_modifier = class_data["skill_modifier"]
        instance._fotitude_bonus_type = class_data["fotitude_bonus_type"]
        instance._will_bonus_type = class_data["will_bonus_type"]
        instance._reflex_save_bonus_type = class_data["reflex_save_bonus_type"]
        instance._class_skills = class_data["class_skills"]
        instance._class_feats = class_data["class_feats"]
        instance._ex_feats = class_data["ex_feats"]
        instance._possible_alignments = class_data["possible_alignments"]
        instance._special = class_data["special"]
        return instance

    def is_alignment_possible(self, alignment):
        return alignment[0] in self.possible_alignments[0] and \
                alignment[1] in self.possible_alignments[1]

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
