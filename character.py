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
        self._classes = list()
        self._race = None
        self._gender = None
        self._age = 0
        self._feat_skill_points = 0
        self._ability_skill_points = 0
        self._level_points = 1
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
        self.__ABILITES = {
            "constitution": self.constitution,
            "con": self.constitution,
            "charisma": self.charisma,
            "cha": self.charisma,
            "dexterity": self.dexterity,
            "dex": self.dexterity,
            "intellect": self.intellect,
            "int": self.intellect,
            "strength": self.strength,
            "str": self.strength,
            "wisdom": self.wisdom,
            "wis": self.wisdom
        }

    def __repr__(self):
        return "<" + self._name + " " + str(self._race) + " " + str(self._classes) + " Level " + str(self.current_level()) + ">"

    def improve_ability(self, abiltiy):
        if self._ability_skill_points < 1:
            return
        if abiltiy == "constitution":
            self._constitution += 1
        if abiltiy == "charisma":
            self._charisma += 1
        if abiltiy == "dexterity":
            self._dexterity += 1
        if abiltiy == "intellect":
            self._intellect += 1
        if abiltiy == "strength":
            self._strength += 1
        if abiltiy == "wisdom":
            self._wisdom += 1
        self._ability_skill_points -= 1

    def add_experience(self, experience):
        level_before = self.current_level()
        self._experience += experience
        delta_level = self.current_level() - level_before
        self._level_points += delta_level

    def set_race(self, race):
        self._race = race

    def add_class_level(self, class_type):
        if self._level_points == 0:
            return
        if not self.has_class(class_type):
            self._classes.append(class_type)
        self._level_points -= 1
        self.class_with_name(class_type._name).level_up(self)

    def class_with_name(self, class_name):
        for class_ in self._classes:
            if class_._name == class_name:
                return class_
        return None

    def has_class(self, class_type):
        return class_type in self._classes

    def ability(self, abiilty_name):
        return self.__ABILITES[abiilty_name]()

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
        for class_ in self._classes:
            if class_.can_learn_skill(skill_name, self):
                return True
        return False

    def can_learn_feat(self, feat_name):
        feat = Feat.with_name(feat_name)
        if feat is None:
            return False
        return feat.has_prequisties(self) and self._feat_skill_points > 0

    def use_skill(self, skill_name):
        skill = self.skill_with_name(skill_name)
        return d20.roll() + skill.level + self.ability_modifier(skill.ability)

    def has_learned_skill(self, skill_name):
        return self.skill_with_name(skill_name).level > 0

    def learn_skill(self, skill_name, times=1):
        if times == 0:
            return
        lowest_cost_class = None
        for class_ in self._classes:
            if class_.can_learn_skill(skill_name, self):
                if class_.is_class_skill(skill_name):
                    lowest_cost_class = class_
                else:
                    if lowest_cost_class is None:
                        lowest_cost_class = class_
        class_.learn_skill(skill_name, self)
        self.learn_skill(skill_name, times - 1)

    def learn_feat(self, feat_name):
        if not self.can_learn_feat(feat_name):
            return
        self._feat_skill_points -= 1
        self._feats.append(Feat.with_name(feat_name))

    def starting_age(self, starting_age_type):
        dice = self._race.starting_age_dice(starting_age_type)
        return self._race._adulthood + dice.roll()

    def relative_age(self):
        if self._age < self._race._middle_age:
            return "young"
        if self._age <= self._race._old_age:
            return "middle"
        if self._age <= self._race._venerable_age:
            return "old"
        return "venerable"

    def roll_height(self):
        return self._race.height(self._gender)

    def roll_weight(self):
        return self._race.weight(self._gender)

    def height(self):
        return core.unit_length * self._height

    def weight(self):
        return core.unit_weight * self._weight

    def has_feat(self, feat_name):
        for feat in self._feats:
            if feat.name.lower() == feat_name.lower():
                return True
        return False

    def __level_up(self):
        self.__increase_skill_points()

    def skill_with_name(self, skill_name):
        for skill in self._skills:
            if skill.name.lower() == skill_name.lower():
                return skill
        return Skill.with_name(skill_name)


class Class(object):

    __ALL_CLASSES = list()

    def __init__(self):
        self._hit_die = None
        self._attack_bonus_type = None
        self._will_save_bonus_type = None
        self._fortitude_save_bonus_type = None
        self._reflex_save_bonus_type = None
        self._skill_modifier = None
        self._name = None
        self._experience = None
        self._skill_points = 0
        self._level = 0
        self._possible_alignments = list()
        self._class_skills = list()
        self._class_feats = list()
        self._ex_feats = list()
        self._special = list()

    def __repr__(self):
        return "<" + self._name + " Level " + str(self._level) + ">"

    def level_up(self, character):
        self._level += 1
        self.__increase_skill_points(character)

    def current_level(self):
        return self._level

    def learn_skill(self, skill_name, character, times=1):
        if not self.can_learn_skill(skill_name, character):
            return
        if self.is_class_skill(skill_name):
            needed_points = 1
        else:
            needed_points = 2
        self._skill_points -= needed_points
        if not character.has_learned_skill(skill_name):
            character._skills.append(character.skill_with_name(skill_name))
        character.skill_with_name(skill_name).level += 1
        if times > 1:
            return self.learn_skill(skill_name, character, times - 1)

    def can_learn_skill(self, skill_name, character):
        current_skill_level = 0
        skill = character.skill_with_name(skill_name)
        current_skill_level = skill.level
        if self.is_class_skill(skill_name):
            max_skill_level = core.class_skill_max_ranks(self.current_level())
            needed_points = 1
        else:
            max_skill_level = core.cross_class_skill_max_ranks(self.current_level())
            needed_points = 2
        return current_skill_level < max_skill_level and self._skill_points > needed_points

    @staticmethod
    def load(data_path):
        data_file = relative_path() + "/" + data_path
        classes = json.loads(open(data_file, encoding="utf-8").read())["classes"]
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
        classes = json.loads(open(data_file, encoding="utf-8").read())["classes"]
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

    def __increase_skill_points(self, character):
        skill_points = (self._skill_modifier + character.intellect_mofifier())
        if self._level == 1:
            skill_points *= 4
            if skill_points < 4:
                skill_points = 4
        self._skill_points += skill_points


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

    def __repr__(self):
        return "<" + self._name + ">"

    @staticmethod
    def load(data_path):
        data_file = relative_path() + "/" + data_path
        races = json.loads(open(data_file, encoding="utf-8").read())["races"]
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


class Feat(object):

    __ALL_FEATS = list()

    def __init__(self, name=None, prequisites=list(), benefit=None):
        self.name = name
        self.prequisites = prequisites
        self.benefit = benefit

    def __repr__(self):
        return "<" + self.name + ">"

    def has_prequisties(self, character):
        for prequisite in self.prequisites:
            if self.__check_prequisite(prequisite, character) == False:
                return False
        return True

    def __check_prequisite(self, prequisite, character):
        if prequisite.startswith("Ability"):
            prequisite = prequisite.split(":")[1].split(" ")
            if prequisite[0] == '':
                prequisite = prequisite[1:]
            ability = prequisite[0]
            value = int(prequisite[1])
            return character.ability(ability) >= value
        if prequisite.startswith("Skill"):
            prequisite = prequisite.split(":")[1].split(" ")
            if prequisite[0] == '':
                prequisite = prequisite[1:]
            skill_name = prequisite[0]
            return character.has_learned_skill(skill_name)
        if prequisite.startswith("Property"):
            prequisite = prequisite.split(":")[1].split(" ")
            if prequisite[0] == '':
                prequisite = prequisite[1:]
            if prequisite[0] == "Level":
                level = int(prequisite[1])
                # TODO: check for class level
                return character.level() >= level
            if prequisite[0] == "Base":  # attack bonus
                attack_bonus = int(prequisite[len(prequisite-1)].replace("+", ""))
                return character.attack_bonus() >= attack_bonus
        return character.has_feat(prequisite)

    @staticmethod
    def available_feats():
        feat_names = list()
        for feat in Feat.__ALL_FEATS:
            feat_names.append(feat.name)
        return feat_names

    @staticmethod
    def with_name(feat_name):
        for feat in Feat.__ALL_FEATS:
            if feat.name.lower() == feat_name.lower():
                return feat
        return None

    @staticmethod
    def load(data_path):
        data_file = relative_path() + "/" + data_path
        feats = json.loads(open(data_file, encoding="utf-8").read())["feats"]
        Feat.__ALL_FEATS = list()
        for feat in feats:
            Feat.__ALL_FEATS.append(Feat(feat["name"], feat["prequisites"], feat["benefit"]))


class Skill(object):

    __ALL_SKILLS = list()

    def __init__(self, name=None, level=0, ability=None, untrained=False):
        self.name = name
        self.level = level
        self.ability = ability
        self.untrained = False

    def __repr__(self):
        return "<" + self.name + " Level " + str(self.level) + ">"

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
        skills = json.loads(open(data_file, encoding="utf-8").read())["skills"]
        Skill.__ALL_SKILLS = list()
        for skill in skills:
            Skill.__ALL_SKILLS.append(Skill(skill["name"], 0, skill["ability"], skill["untrained"]))
