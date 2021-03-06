import copy
import json
import os

from .combatant import Combatant
from .core import *
from .dice import *


# Character sheet
class Character(Combatant):
    """
    :type _name: str
    :type _alignment: str[]
    :type _skills: Skill[]
    :type _feats: Feat[]
    :type _classes: Class[]
    :type _race: Race
    :type _gender: str
    :type _age: int
    :type _feat_skill_points: int
    :type _weight: int
    :type _height: int
    :type _ability_skill_points: int
    :type _level_points: int
    :type _hit_points: dict
    """

    __AGE_MODIFIER = {
        "young": 0,
        "middle": 1,
        "old": 2,
        "venerable": 3
    }

    def __init__(self, name="", *args, **kwargs):
        """
        Creates a Character object
        :param name: The name of the character
        """
        Combatant.__init__(self, name, *args, **kwargs)

        self._weight = 0
        self._height = 0
        # Maps class type to a level
        self._classes = {}
        self._items = {}
        self._skills = {}
        self._race = None

    def __repr__(self):
        return "<" + self._name + ">"
        #return "<" + self._name + " lvl" + str(self.current_level()) + ">"

    # Calculate effective level
    def current_level(self):
        result = 0
        for cls, level in self._classes.items():
            result += level
        return result

    def get_class_level(self, class_name):
        """
        :param str class_name: required character class name
        :return:
        """
        for cls, level in self._classes.items():
            if cls.name == class_name:
                return level
        return 0

    # Add level to character
    def add_class_level(self, new_class, levels = 1, **kwargs):
        old_level = 0
        feats = kwargs.get('feats', [])
        # Get old level
        if new_class in self._classes:
            old_level = self._classes[new_class]
        # Apply changes
        new_class.apply(self, old_level, old_level + levels)
        # Move effective level
        if new_class in self._classes:
            self._classes[new_class] += levels
        else:
            self._classes[new_class] = levels

        for feat in feats:
            self.add_feat(feat)

    def max_hit_points(self):
        """
        returns the maximum hit points

        :rtype: int
        """
        return self._hit_points["maximum"]

    def set_race(self, race):
        """
        Sets the race

        :param Race race: The race to set
        """
        self._race = race
        for i in range(0, 6):
            self._stats[i] += race._stats[i]

    def class_with_name(self, class_name):
        """
        returns the class with the given name if the character has it

        :param str class_name: The name of the class
        :rtype: Class | None
        """
        for class_ in self._classes:
            if class_.name == class_name:
                return class_
        return None

    def has_class(self, class_type):
        """
        checks whether the character has a class of a specific type or not

        :param Class class_type: The name of the class
        :rtype: bool
        """
        return class_type in self._classes

    def can_learn_skill(self, skill_name):
        """
        checks whether a skill can be learned

        :param str skill_name: The name of the skill
        :rtype: bool
        """
        for class_ in self._classes:
            if class_.can_learn_skill(skill_name, self):
                return True
        return False

    def use_skill(self, skill_name):
        """
        Rolls the skill
        d20 + current level of the skill + ability modifier of the skill

        :param str skill_name: The name of the skill
        :rtype: int
        """
        skill = self.skill_with_name(skill_name)
        return d20.roll() + skill.level + self.ability_modifier(skill.ability)

    def has_learned_skill(self, skill_name):
        """
        checks whether a skill has been learned

        :param str skill_name: The name of the skill
        :rtype: bool
        """
        skill = self.skill_with_name(skill_name)
        return skill is not None and skill.level > 0

    def learn_skill(self, skill_name, times=1):
        """
        learns a skill

        :param str skill_name: The name of the skill
        :param int times: Amount of levels to add to the skill
        """
        if times == 0:
            return
        lowest_cost_class = None
        for class_ in self._classes:
            if class_.can_learn_skill(skill_name, self):
                if lowest_cost_class is None:
                    lowest_cost_class = class_
                if class_.is_class_skill(skill_name):
                    lowest_cost_class = class_
        if lowest_cost_class is None:
            return
        lowest_cost_class.learn_skill(skill_name, self)
        self.learn_skill(skill_name, times - 1)

    def starting_age(self, starting_age_type):
        """
        Calculates the adulthood starting age depending on the type of starting age

        :param str starting_age_type: The type of starting age
        """
        dice = self._race.starting_age_dice(starting_age_type)
        return self._race._adulthood + dice.roll()

    def relative_age(self):
        """
        Returns the relative age of the character. A 14 years old human would be relatively "young".
        possible results are "young", "middle", "old" and "venerable".

        :rtype: str
        """
        if self._age < self._race._middle_age:
            return "young"
        if self._age <= self._race._old_age:
            return "middle"
        if self._age <= self._race._venerable_age:
            return "old"
        return "venerable"

    def roll_height(self):
        """
        Rolls the height depending on the gender and race of this character

        :rtype: float
        """
        return self._race.height(self._gender)

    def roll_weight(self):
        """
        Rolls the weight depending on the gender and race of this character

        :rtype: float
        """
        return self._race.weight(self._gender)

    def height(self):
        """
        Returns the height of the character in the current unit.

        :rtype: float
        """
        return unit_length * self._height

    def weight(self):
        """
        Returns the weight of the character in the current unit.

        :rtype: float
        """
        return unit_weight * self._weight

    def feats(self):
        """
        Returns all learned feats

        :rtype: Feat[]
        """
        feats = list()
        feats += self._feats
        for class_ in self._classes:
            feats += class_.feats()
        return feats

    def get_feat_type(self, feat_type):
        """
        Checks whether a feat has been learned

        :param class feat_type: Class type of the feat
        :rtype: bool
        """
        result = []
        for feat in self.feats():
            if isinstance(feat, feat_type):
                result.append(feat)
        return result

    def skill_with_name(self, skill_name):
        """
        Returns a learned skill with the given name or None if the skill can not be found

        :param str skill_name: The name of the skill
        :rtype: Skill
        """
        for skill in self._skills:
            if skill.name.lower() == skill_name.lower():
                return skill
        return Skill.with_name(skill_name)

    def armor_class(self):
        """
        Calculates the current armor class

        :rtype: int
        """
        armor_bonus = 0     # TODO: implement equipment
        shield_bonus = 0    # TODO: implement equipment
        return 10 + armor_bonus + shield_bonus + ac_size_modifier(self._height) + self.dexterity_modifier()

    def size_category(self):
        """
        Returns the size category

        :rtype: str
        """
        return size_category(self._height)


# Level-dependent progression
# Class consists of several progression types, like BAB, saving throw, HP, ...
class Progression(object):
    def __init__(self):
        pass

    # Apply progression
    def apply(self, character, level_from, level_to):
        pass


class CharacterClass(object):
    """
    Encapsulates character class
    Character class contains a set of 'progressions' and per-level feats,
    which define class features
    :type _name: str
    """
    def __init__(self, name, *args):
        """
        Creates a Class object
        """
        self._name = name
        self._progressions = []

        for arg in args:
            if isinstance(arg, Progression):
                self._progressions.append(arg)

    @property
    def name(self):
        return self._name

    # Apply class changes for level up
    def apply(self, character, level_from, level_to):
        for p in self._progressions:
            p.apply(character, level_from, level_to)

    def learn_skill(self, skill_name, character, times=1):
        """
        Learns a skill for a character

        :param str skill_name: The name of the skill to learn
        :param Character character: The character that learns the skill
        :param int times: Amount of levels to learn
        """
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
        """
        Checks whether a skill can be learned

        :param str skill_name: The name of the skill to learn
        :param Character character: The character to check the skill for
        :rtype: bool
        """
        skill = character.skill_with_name(skill_name)
        current_skill_level = skill.level
        if self.is_class_skill(skill_name):
            max_skill_level = class_skill_max_ranks(self.current_level())
            needed_points = 1
        else:
            max_skill_level = cross_class_skill_max_ranks(self.current_level())
            needed_points = 2
        return current_skill_level < max_skill_level and self._skill_points > needed_points

    def is_alignment_possible(self, alignment):
        """
        Checks whether an alignment is possible for the current class.

        :param str alignment: The alignment
        :rtype: bool
        """
        return alignment[0] in self._possible_alignments[0] and \
            alignment[1] in self._possible_alignments[1]

    def skill_points(self, int_modifier):
        """
        Calculate the amount of skill points

        :param int int_modifier: The int modifier
        :rtype: int
        """
        if int_modifier < 0:
            int_modifier = 0
        return self._skill_modifier + int_modifier

    def is_class_skill(self, skill_name):
        """
        Checks whether a skill is a class-skill

        :param str skill_name: The name of the skill
        :rtype: bool
        """
        for skill in self._class_skills:
            if skill.lower() == skill_name.lower():
                return True
        return False

    def __increase_skill_points(self, character):
        skill_points = (self._skill_modifier + character.intellect_modifier())
        # only the first class gets the initial skill bonus
        if self._level == 1 and len(character._classes) == 1:
            skill_points *= 4
            if skill_points < 4:
                skill_points = 4
        self._skill_points += skill_points

    def __repr__(self):
        return "<" + self._name + " Level " + str(self._level) + ">"


class Feat(object):
    """
    :type name: str
    :type prerequisites: list
    :type _benefit: str
    """

    class FeatData:
        """
        FeatData

        Contains strings for a feat, like description and benefit
        """
        def __init__(self):
            self.description = "empty description"
            self.benefit = "empty benefit"
            self.name = "FeatName"
            self.requirements = []

    # Dictionary of all feat types.
    # But we create feat instance for every combatant!
    __ALL_FEATS = dict()

    # Feat requirements
    # TODO: Implement feat requirement system
    REQUIRE_FEATS = 1
    REQUIRE_BAB = 2
    REQUIRE_STAT = 3
    REQUIRE_SKILL = 4

    def __init__(self, name, prerequisites=list(), **kwargs):
        """
        Creates a Feat object

        :param str name: The name of the feat
        :param str[] prerequisites: Prerequisites of the feat
        :param str benefit: The benefit of the feat
        """
        self._name = name
        self.prerequisites = prerequisites
        self._benefit = kwargs.get('benefit', "")
        self._priority = 100
        #Feat.__ALL_FEATS[]

    @property
    def name(self):
        return self._name

    @property
    def priority(self):
        return self._priority

    @staticmethod
    def available_feats():
        """
        Lists all names of loaded feats.

        :rtype: str[]
        """
        feat_names = list()
        for feat in Feat.__ALL_FEATS:
            feat_names.append(feat.name)
        return feat_names

    @staticmethod
    def with_name(feat_name):
        """
        Returns a feat with the given name if one is loaded.

        :param str feat_name: The name of the feat
        :rtype: Feat | None
        """
        for feat in Feat.__ALL_FEATS:
            if feat.name.lower() == feat_name.lower():
                return copy.deepcopy(feat)
        return None

    @staticmethod
    def load(data_path):
        """
        Loads feats from a data file. This method should be called when initializing a package that contains
        game specific feat data.

        :param str data_path: The path to the data file in json format, relative to the root package
        """
        data_file = relative_path() + "/" + data_path
        feats = json.loads(open(data_file, encoding="utf-8").read())["feats"]
        Feat.__ALL_FEATS = list()
        for feat in feats:
            Feat.__ALL_FEATS.append(Feat(feat["name"], feat["prerequisites"], feat["benefit"]))

    def has_prerequisites(self, character):
        """
        Checks whether the feat has prerequisites

        :param Character character: The character using the feat
        :rtype: bool
        """
        for prerequisite in self.prerequisites:
            if not self.__check_prerequisite(prerequisite, character):
                return False
        return True

    def __check_prerequisite(self, prequisite, character):
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
                return character.current_level() >= level
            if prequisite[0] == "Base":  # attack bonus
                attack_bonus = int(prequisite[len(prequisite)-1].replace("+", ""))
                return character.attack_bonus() >= attack_bonus
        return character.has_feat(prequisite)

    def __repr__(self):
        return "<" + self.name + ">"

    def __str__(self):
        return "<" + self.name + ">"

    def apply(self, combatant: Combatant):
        pass


class Skill(object):
    """
    :type name: str
    :type level: int
    :type ability: str
    :type untrained: bool
    """

    __ALL_SKILLS = list()

    def __init__(self, name="noskill", **kwargs):
        """
        Creates a Skill instance

        :param str name: The name of the skill
        :param int level: The level of the skill
        :param str ability: The ability of the skill
        :param bool untrained: Whether the skill can be used untrained
        """
        self._name = name
        self.ability = kwargs.get('ability', STAT_CHA)
        self.trained = kwargs.get('trained', False)
        self.armor_penalty = kwargs.get('armor', False)

    def __repr__(self):
        return "<" + self._name + ">"

    @property
    def name(self):
        return self._name

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    @staticmethod
    def available_skills():
        """
        Lists all names of loaded skills.

        :rtype: str[]
        """
        skill_names = list()
        for skill in Skill.__ALL_SKILLS:
            skill_names.append(skill.name)
        return skill_names

    @staticmethod
    def with_name(skill_name):
        """
        Returns a skill with the given name if one is loaded.

        :param str skill_name: The name of the feat
        :rtype: Skill | None
        """
        for skill in Skill.__ALL_SKILLS:
            if skill.name.lower() == skill_name.lower():
                return copy.deepcopy(skill)
        return None