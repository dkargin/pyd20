from unittest import TestCase
from battle.character import Character, Feat
from battle.core import *
import battle.dice as dice
import dnd
import random
import math

unit_length = UNIT_LENGTH_METER
unit_weight = UNIT_WEIGHT_KILOGRAM


class CharacterTest(TestCase):

    def __roll_ability_score(self):
        results = list()
        for i in range(0, 3):
            results.append(dice.d6.roll())
        results.sort(reverse=True)
        return sum(results[:3])

    def __random_race(self):
        races = [dnd.human, dnd.elf, dnd.gnome, dnd.half_elf, dnd.half_orc, dnd.halfling]
        return races[math.floor(random.random() * len(races))]

    def __random_class(self):
        classes = [
            dnd.barbarian, dnd.bard, dnd.druid, dnd.cleric, dnd.sorcerer,
            dnd.wizard, dnd.rogue, dnd.monk, dnd.paladin, dnd.fighter
        ]
        return classes[math.floor(random.random() * len(classes))]

    def __random_gender(self):
        genders = [GENDER_FEMALE, GENDER_MALE]
        return genders[math.floor(random.random() * len(genders))]

    def __random_skill(self):
        skills = Skill.available_skills()
        return skills[math.floor(random.random() * len(skills))]

    def __random_feat(self):
        feats = Feat.available_feats()
        return feats[math.floor(random.random() * len(feats))]

    def random_character(self):
        random_character = Character("Random Character")
        random_character.set_race(self.__random_race())

        # apply base stats
        random_character._strength = self.__roll_ability_score()
        random_character._wisdom = self.__roll_ability_score()
        random_character._charisma = self.__roll_ability_score()
        random_character._intellect = self.__roll_ability_score()
        random_character._dexterity = self.__roll_ability_score()
        random_character._constitution = self.__roll_ability_score()

        # add xp to be able to add class levels
        random_character.add_experience(5000)

        # assign class levels
        random_class = self.__random_class()
        for i in range(0, 10):
            random_character.add_class_level(random_class)

        random_character._gender = self.__random_gender()
        random_character._age = random_character.starting_age(random_character._classes[0]._starting_age_type)
        random_character._height = random_character.roll_height()
        random_character._weight = random_character.roll_weight()

        for i in range(0, 1 + math.floor(random.random() * 2)):
            random_character.learn_skill(self.__random_skill())

        random_character.learn_feat(self.__random_feat())
        return random_character

    def test_character(self):
        for i in range(0, 10):
            char = self.random_character()
            print(char.print_character())

        """
        print("str\t\t", tenlon.strength())
        print("wis\t\t", tenlon.wisdom())
        print("cha\t\t", tenlon.charisma())
        print("int\t\t", tenlon.intellect())
        print("dex\t\t", tenlon.dexterity())
        print("con\t\t", tenlon.constitution())
        print("age\t\t", tenlon._age)
        print("hp\t\t", tenlon.hit_points())
        print("age-type", tenlon.relative_age())
        print("height\t", tenlon.height(), "m")
        print("weight\t", tenlon.weight(), "kg")
        print("skills\t", tenlon._skills)
        print("feats\t", tenlon.feats())
        print(tenlon._skills[0].name + "\t", tenlon.use_skill(tenlon._skills[0].name))
        """

