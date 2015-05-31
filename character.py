#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
from pyd20.dice import Dice, d20
import pyd20.core as core

# constants for alignment
ALIGNMENT_GOOD = "Good"
ALIGNMENT_NEUTRAL = "Neutral"
ALIGNMENT_EVIL = "Evil"
ALIGNMENT_CHAOTIC = "Chaotic"
ALIGNMENT_LAWFUL = "Lawful"


# auxiliary function
def relative_path():
    parts = os.path.realpath(__file__).split("/")
    parts = parts[:len(parts) - 1]
    return "/".join(parts)


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
        self._experience = 0
        self._name = None
        self._alignment = [None, None]
        self._skills = list()
        self._feats = list()
        self._class = None
        self.__ABILITIY_MODIFIER = {
            "constitution": self.constitution_mofifier,
            "con": self.constitution_mofifier,
            "charisma": self.charisma_mofifier,
            "cha": self.charisma_mofifier,
            "dexterity": self.dexterity_mofifier,
            "dex": self.dexterity_mofifier,
            "intellect": self.intellect_mofifier,
            "int": self.intellect_mofifier,
            "strength": self.strength_modifier,
            "str": self.strength_modifier,
            "wisdom": self.wisdom_mofifier,
            "wis": self.wisdom_mofifier
        }

    def set_class(self, class_type):
        self._class = class_type

    def constitution_mofifier(self):
        return core.ability_modifier(self._constitution)

    def charisma_mofifier(self):
        return core.ability_modifier(self._charisma)

    def dexterity_mofifier(self):
        return core.ability_modifier(self._dexterity)

    def intellect_mofifier(self):
        return core.ability_modifier(self._intellect)

    def strength_modifier(self):
        return core.ability_modifier(self._strength)

    def wisdom_mofifier(self):
        return core.ability_modifier(self._wisdom)

    def ability_modifier(self, ability):
        return self.__ABILITIY_MODIFIER[ability]()

    def current_level(self):
        return core.current_level(self._experience)

    def can_learn_skill(self, skill_name):
        current_skill_level = 0
        skill = self.__skill_by_name(skill_name)
        current_skill_level = skill.level
        if self._class.is_class_skill(skill_name):
            max_skill_level = core.class_skill_max_ranks(self._level)
        else:
            max_skill_level = core.cross_class_skill_max_ranks(self._level)
        return current_skill_level < max_skill_level

    def use_skill(self, skill_name):
        skill = self.__skill_with_name(skill_name)
        return d20.roll() + skill.level + self.ability_modifier(skill.ability)

    def has_trained_skill(self, skill_name):
        return self.__skill_with_name(skill_name).level > 0

    def __skill_with_name(self, skill_name):
        for skill in self._skills:
            if skill.name.lower() == skill_name.lower():
                return skill
        return Skill.skill_with_name(skill_name)


class Skill(object):

    __ALL_SKILLS = list()
    __SKILL_DATA = "data/skills.json"

    def __init__(self, name=None, level=0, ability=None, untrained=False):
        self.name = name
        self.level = level
        self.ability = ability
        self.untrained = False

    @staticmethod
    def available_skills():
        skill_names = list()
        for skill in Skill.__ALL_SKILLS:
            skill_names.append(skill.name)
        return skill_names

    @staticmethod
    def skill_with_name(skill_name):
        for skill in Skill.__ALL_SKILLS:
            if skill.name.lower() == skill_name.lower():
                return skill
        return None

    @staticmethod
    def load():
        data_file = relative_path() + "/" + Skill.__SKILL_DATA
        skills = json.loads(open(data_file).read())["skills"]
        Skill.__ALL_SKILLS = list()
        for skill in skills:
            Skill.__ALL_SKILLS.append(Skill(skill["name"], 0, skill["ability"], skill["untrained"]))

Skill.load()


class Class(object):

    """
    implements a class
    """

    CLASS_DATA = "data/classes.json"

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
        data_file = relative_path() + "/" + Class.CLASS_DATA
        classes = json.loads(open(data_file).read())["classes"]
        class_data = None
        for c in classes:
            if c["class_name"].lower() == class_name.lower():
                class_data = c
                break
        instance = Class()
        instance._name = class_data["class_name"]
        instance._hit_die = Dice.from_string(class_data["hit_die"])
        instance._attack_bonus_type = class_data["attack_bonus_type"]
        instance._skill_modifier = class_data["skill_modifier"]
        instance._fotitude_save_bonus_type = class_data["fotitude_bonus_type"]
        instance._will_save_bonus_type = class_data["will_bonus_type"]
        instance._reflex_save_bonus_type = class_data["reflex_bonus_type"]
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

    def is_class_skill(self, skill_name):
        for skill in self._class_skills:
            if skill.lower() == skill_name.lower():
                return True
        return False

    @staticmethod
    def available_classes():
        data_file = relative_path() + "/" + Class.CLASS_DATA
        classes = json.loads(open(data_file).read())["classes"]
        class_names = list()
        for c in classes:
            class_names.append(c["class_name"])
        return class_names
