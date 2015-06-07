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

GENDER_MALE = "male"
GENDER_FEMALE = "female"


# auxiliary function
def relative_path():
    parts = os.path.realpath(__file__).split("/")
    parts = parts[:len(parts) - 1]
    return "/".join(parts)


class Character(object):

    """
    implements a character
    """

    __AGE_MODIFIER = {
        "young": 0,
        "middle": 1,
        "old": 2,
        "venerable": 3
    }

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
        self._race = None
        self._gender = None
        self._age = 0
        self._skill_points = 0
        self._feat_skill_points = 0
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

    def maximum_skill_points(self):
        skill_points = 0
        for level in range(1, self.current_level() + 1):
            skill_points += (self._class._skill_modifier + self.intellect_mofifier())
            if level == 1:
                skill_points *= 4
                if skill_points < 4:
                    skill_points = 4
        return skill_points

    def set_race(self, race):
        self._race = race

    def set_class(self, class_type):
        self._class = class_type

    def constitution(self):
        age_modifier = self.__AGE_MODIFIER[self.relative_age()]
        return self._constitution - age_modifier

    def charisma(self):
        age_modifier = self.__AGE_MODIFIER[self.relative_age()]
        return self._charisma + age_modifier

    def dexterity(self):
        age_modifier = self.__AGE_MODIFIER[self.relative_age()]
        return self._dexterity - age_modifier

    def intellect(self):
        age_modifier = self.__AGE_MODIFIER[self.relative_age()]
        return self._intellect + age_modifier

    def strength(self):
        age_modifier = self.__AGE_MODIFIER[self.relative_age()]
        return self._strength - age_modifier

    def wisdom(self):
        age_modifier = self.__AGE_MODIFIER[self.relative_age()]
        return self._wisdom + age_modifier

    def constitution_mofifier(self):
        return core.ability_modifier(self.constitution())

    def charisma_mofifier(self):
        return core.ability_modifier(self.charisma())

    def dexterity_mofifier(self):
        return core.ability_modifier(self.dexterity())

    def intellect_mofifier(self):
        return core.ability_modifier(self.intellect())

    def strength_modifier(self):
        return core.ability_modifier(self.strength())

    def wisdom_mofifier(self):
        return core.ability_modifier(self.wisdom())

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

    def starting_age(self):
        dice = self._race.starting_age_dice(self._class._starting_age_type)
        return self._race._adulthood + dice.roll()

    def relative_age(self):
        if self._age < self._race._middle_age:
            return "young"
        if self._age <= self._race._old_age:
            return "middle"
        if self._age <= self._race._venerable_age:
            return "old"
        return "venerable"

    def __skill_with_name(self, skill_name):
        for skill in self._skills:
            if skill.name.lower() == skill_name.lower():
                return skill
        return Skill.with_name(skill_name)

    def roll_height(self):
        return self._race.height(self._gender)

    def roll_weight(self):
        return self._race.weight(self._gender)

    def height(self):
        return core.unit_length * self._height

    def weight(self):
        return core.unit_weight * self._weight


class Class(object):

    """
    implements a class
    """

    __ALL_CLASSES = list()

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
    def load(data_path):
        data_file = relative_path() + "/" + data_path
        classes = json.loads(open(data_file).read())["classes"]
        Class.__ALL_CLASSES = list()
        for class_data in classes:
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
            instance._starting_age_type = class_data["starting_age_type"]
            Class.__ALL_CLASSES.append(instance)

    @staticmethod
    def with_name(class_name):
        for c in Class.__ALL_CLASSES:
            if c._name.lower() == class_name.lower():
                return c
        return None

    @staticmethod
    def available_classes():
        data_file = relative_path() + "/" + Class.CLASS_DATA
        classes = json.loads(open(data_file).read())["classes"]
        class_names = list()
        for c in classes:
            class_names.append(c["class_name"])
        return class_names

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


class Race(object):

    __ALL_RACES = list()

    def __init__(self):
        self._name = None
        self._middle_age = 0
        self._old_age = 0
        self._venerable_age = 0
        self._maximum_age = 0
        self._adulthood = 0
        self._starting_age_young = 0
        self._starting_age_medium = 0
        self._starting_age_old = 0
        self._height_modifier_roll = None

    @staticmethod
    def load(data_path):
        data_file = relative_path() + "/" + data_path
        races = json.loads(open(data_file).read())["races"]
        Race.__ALL_RACES = list()
        for race in races:
            instance = Race()
            instance._name = race["name"]
            instance._middle_age = race["middle_age"]
            instance._old_age = race["old_age"]
            instance._venerable_age = race["venerable_age"]
            instance._maximum_age = Dice.from_string(race["maximum_age"])
            instance._adulthood = race["adulthood"]
            instance._starting_age_young = Dice.from_string(race["starting_age_young"])
            instance._starting_age_medium = Dice.from_string(race["starting_age_medium"])
            instance._starting_age_old = Dice.from_string(race["starting_age_old"])
            instance._body = {
                "male": race["body"]["male"],
                "female": race["body"]["female"]
            }
            Race.__ALL_RACES.append(instance)

    @staticmethod
    def with_name(race_name):
        for race in Race.__ALL_RACES:
            if race._name.lower() == race_name.lower():
                return race
        return None

    def height(self, gender):
        body = self._body[gender]
        modifier_dice = Dice.from_string(body["height_modifier"])
        self._height_modifier_roll = modifier_dice.roll()
        return body["base_height"] + (float(self._height_modifier_roll) / 12)  # calculating in inch

    def weight(self, gender):
        if self._height_modifier_roll is None:
            self.height(gender)
        modifier_dice = Dice.from_string(self._body[gender]["weight_modifier"])
        return self._body[gender]["base_weight"] + (self._height_modifier_roll * modifier_dice.roll())

    def starting_age_dice(self, age_type):
        if age_type == "young":
            return self._starting_age_young
        if age_type == "medium":
            return self._starting_age_medium
        if age_type == "old":
            return self._starting_age_old


class Skill(object):

    __ALL_SKILLS = list()

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
    def with_name(skill_name):
        for skill in Skill.__ALL_SKILLS:
            if skill.name.lower() == skill_name.lower():
                return skill
        return None

    @staticmethod
    def load(data_path):
        data_file = relative_path() + "/" + data_path
        skills = json.loads(open(data_file).read())["skills"]
        Skill.__ALL_SKILLS = list()
        for skill in skills:
            Skill.__ALL_SKILLS.append(Skill(skill["name"], 0, skill["ability"], skill["untrained"]))
