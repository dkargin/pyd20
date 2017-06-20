import json
import os
import core
import copy

from dice import d20, Dice, Die
from battle.battle import Combatant

ALIGNMENT_GOOD = "Good"
ALIGNMENT_NEUTRAL = "Neutral"
ALIGNMENT_EVIL = "Evil"
ALIGNMENT_CHAOTIC = "Chaotic"
ALIGNMENT_LAWFUL = "Lawful"

GENDER_MALE = "male"
GENDER_FEMALE = "female"

def relative_path():
    """
    auxiliary function to retrieve the relative path to the current script
    :rtype: str
    """
    path = os.path.realpath(__file__)
    if "nt" in os.name:
        parts = path.split("\\")
    else:
        parts = path.split("/")
    parts = parts[:len(parts) - 1]
    return "/".join(parts)

# Character sheet
class Character(Combatant):

    """
    :type _constitution: int
    :type _charisma: int
    :type _dexterity: int
    :type _intellect: int
    :type _strength: int
    :type _wisdom: int
    :type _experience: int
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

    def __init__(self, name=""):
        """
        Creates a Character object
        :param name: The name of the character
        """
        Combatant.__init__(self)

        self._name = name

        self._weight = 0
        self._height = 0

        '''
        self._hit_points = {
            "current": 0,
            "maximum": 0
        }

        self.__ABILITY_MODIFIER = {
            "constitution": self.constitution_mofifier,
            "con": self.constitution_mofifier,
            "charisma": self.charisma_mofifier,
            "cha": self.charisma_mofifier,
            "dexterity": self.dexterity_mofifier,
            "dex": self.dexterity_mofifier,
            "intellect": self.intellect_mofifier,
            "intelligence": self.intellect_mofifier,
            "int": self.intellect_mofifier,
            "strength": self.strength_modifier,
            "str": self.strength_modifier,
            "wisdom": self.wisdom_mofifier,
            "wis": self.wisdom_mofifier
        }
        self.__ABILITIES = {
            "constitution": self.constitution,
            "con": self.constitution,
            "charisma": self.charisma,
            "cha": self.charisma,
            "dexterity": self.dexterity,
            "dex": self.dexterity,
            "intellect": self.intellect,
            "intelligence": self.intellect,
            "int": self.intellect,
            "strength": self.strength,
            "str": self.strength,
            "wisdom": self.wisdom,
            "wis": self.wisdom
        }
        '''

    def __repr__(self):
        return "<" + self._name + " Level " + str(self.current_level()) + ">"

    def hit_points(self):
        """
        returns the current hit points

        :rtype: int
        """
        return self._hit_points["current"]

    def get_name(self):
        return self._name

    def max_hit_points(self):
        """
        returns the maximum hit points

        :rtype: int
        """
        return self._hit_points["maximum"]

    def add_experience(self, experience):
        """
        adds experience points, and levels up if enough xp is gained

        :param int experience: Amount of xp to add
        """
        level_before = self.current_level()
        self._experience += experience
        delta_level = self.current_level() - level_before
        self._level_points += delta_level
        self._feat_skill_points += int(self.current_level()/3) - int(level_before/3)
        self._ability_skill_points += int(self.current_level()/4) - int(level_before/4)

    def set_race(self, race):
        """
        Sets the race

        :param Race race: The race to set
        """
        self._race = race

    def add_class_level(self, class_type, times=1):
        """
        Adds a level to a class if enough level points are available.

        :param Class class_type: The class type to level up
        :param int times: Amount of levels to add.
        """
        if times == 0:
            return
        if self._level_points == 0:
            return
        if not self.has_class(class_type):
            self._classes.append(copy.deepcopy(class_type))
        self._level_points -= 1
        self.class_with_name(class_type._name).level_up(self)
        self.add_class_level(class_type, times - 1)

        # removes empty dummy classes
        for cls in self._classes:
            if cls.current_level() == 0:
                self._classes.remove(cls)

    def class_with_name(self, class_name):
        """
        returns the class with the given name if the character has it

        :param str class_name: The name of the class
        :rtype: Class | None
        """
        for class_ in self._classes:
            if class_._name == class_name:
                return class_
        return None

    def has_class(self, class_type):
        """
        checks whether the character has a class of a specific type or not

        :param Class class_type: The name of the class
        :rtype: bool
        """
        return class_type in self._classes


    def current_level(self):
        """
        returns the current level

        :rtype: int
        """
        return core.current_level(self._experience)

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

    def can_learn_feat(self, feat_name):
        """
        checks whether a feat can be learned

        :param str feat_name: The name of the skill
        :rtype: bool
        """
        feat = Feat.with_name(feat_name)
        if feat is None:
            return False
        return feat.has_prerequisites(self) and self._feat_skill_points > 0

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

    def learn_feat(self, feat_name):
        """
        learns a feat

        :param str feat_name: The name of the feat
        """
        if not self.can_learn_feat(feat_name):
            return
        self._feat_skill_points -= 1
        self._feats.append(Feat.with_name(feat_name))

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
        return core.unit_length * self._height

    def weight(self):
        """
        Returns the weight of the character in the current unit.

        :rtype: float
        """
        return core.unit_weight * self._weight

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

    def has_feat(self, feat_name):
        """
        Checks whether a feat has been learned

        :param str feat_name: The name of the feat
        :rtype: bool
        """
        for feat in self.feats():
            if feat.name.lower() == feat_name.lower():
                return True
        return False

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
        return 10 + armor_bonus + shield_bonus + core.ac_size_modifier(self._height) + self.dexterity_mofifier()

    def initiative(self):
        """
        Calculates the initiative

        :rtype: int
        """
        return d20.roll() + self.dexterity_mofifier()

    def size_category(self):
        """
        Returns the size category

        :rtype: str
        """
        return core.size_category(self._height)

    def attack_bonus(self):
        """
        Calculates the maximum attack bonus for this character
        """
        attack_bonus = 0
        for cls in self._classes:
            cls_attack_bonus = cls.attack_bonus(cls.current_level())
            if cls_attack_bonus > attack_bonus:
                attack_bonus = cls_attack_bonus
        return attack_bonus


class Progression(object):
    def __init__(self):
        pass

    # Apply progression
    def apply(self, character, level_from, level_to):
        pass


# Progression for base attack bonus
# LOW = 0
# MEDIUM = 1
# HIGH = 2
class ProgressionBAB(Progression):
    def __init__(self, speed):
        self.speed = speed

    def calculate(self, level):
        if self.speed == 0:
            return level / 2
        elif self.speed == 1:
            return (level * 3) / 4
        else:
            return level

    def apply(self, character, level_from, level_to):
        character.attack_bonus += (self.calculate(level_to) - self.calculate(level_from))


class ProgressionSaveThrow(Progression):
    def __init__(self, fort, ref, will):
        self.fort = fort
        self.ref = ref
        self.will = will

    def calculate(self, level, flag):
        return 2 + level / 2 if flag else level / 3

    def apply(self, character, level_from, level_to):
        character._save_fort += (self.calculate(level_to, self.fort) - self.calculate(level_from, self.fort))
        character._save_ref += (self.calculate(level_to, self.ref) - self.calculate(level_from, self.ref))
        character._save_will += (self.calculate(level_to, self.will) - self.calculate(level_from, self.will))


class ProgressionHP(Progression):
    def __init__(self, dice):
        self.dice = dice

    def apply(self, character, level_from, level_to):
        HP = character.constitution_mofifier() * (level_to - level_from)
        if level_from == 0:
            HP += self.dice
            level_to-= 1
        dice = Dice()
        for a in range(level_to):
            dice.add_die(Die(self.dice))

        HP += dice.roll()
        character._health_max += HP


class Class(object):
    """
    :type _hit_die: Die
    :type _attack_bonus_type: str
    :type _will_save_bonus_type: str
    :type _fortitude_save_bonus_type: str
    :type _reflex_save_bonus_type: str
    :type _skill_modifier: int
    :type _name: str
    :type _experience: int
    :type _skill_points: int
    :type _level: int
    :type _possible_alignments: str[]
    :type _class_skills: Skill[]
    :type _class_feats: ClassFeat[]
    :type _ex_feats: Feat[]
    :type _special: str
    """

    def __init__(self, progressions):
        """
        Creates a Class object
        """
        self._BAB = 0
        self._hit_die = None
        self._will_save_bonus_type = None
        self._fortitude_save_bonus_type = None
        self._reflex_save_bonus_type = None
        self._skill_modifier = None
        self._name = None
        self._experience = None
        self._skill_points = 0
        self._level = 0
        self._progressions = []

    @staticmethod
    def load(data_path):
        """
        Loads classes from a data file. This method should be called when initializing a package that contains
        game specific class data.

        :param str data_path: The path to the data file in json format, relative to the root package
        """
        data_file = relative_path() + "/" + data_path
        classes = json.loads(open(data_file, encoding="utf-8").read())["classes"]
        Class.__ALL_CLASSES = list()
        for class_data in classes:
            instance = Class()
            instance._name = class_data["class_name"]
            instance._hit_die = Dice.from_string(class_data["hit_die"])
            instance._attack_bonus_type = class_data["attack_bonus_type"]
            instance._skill_modifier = class_data["skill_modifier"]
            instance._fortitude_save_bonus_type = class_data["fortitude_bonus_type"]
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
    def available_classes():
        """
        Returns the list of names for all available classes.

        :rtype: str[]
        """
        class_names = []
        for cls in Class.__ALL_CLASSES:
            class_names.append(cls._name)
        return class_names

    def level_up(self, character):
        """
        Applies a class level up bonus to a character

        :param Character character: The character to apply the bonus to
        """
        self._level += 1
        self.__increase_skill_points(character)
        self.__increase_health(character)

    def current_level(self):
        """
        Returns the current level of this class

        :rtype: int
        """
        return self._level

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
            max_skill_level = core.class_skill_max_ranks(self.current_level())
            needed_points = 1
        else:
            max_skill_level = core.cross_class_skill_max_ranks(self.current_level())
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

    def attack_bonus(self, level):
        """
        Calculates the attack bonus for a given level

        :param int level: The level
        :rtype: int
        """
        return core.attack_bonus(level, self._attack_bonus_type)[0]

    def will_save_bonus(self, level):
        """
        Calculates the will save bonus for a given level

        :param int level: The level
        :rtype: int
        """
        return core.save_bonus(level, self._will_save_bonus_type)

    def fortitude_save_bonus(self, level):
        """
        Calculates the fortitude save bonus for a given level

        :param int level: The level
        :rtype: int
        """
        return core.save_bonus(level, self._fortitude_save_bonus_type)

    def reflex_save_bonus(self, level):
        """
        Calculates the reflex save bonus for a given level

        :param int level: The level
        :rtype: int
        """
        return core.save_bonus(level, self._reflex_save_bonus_type)

    def roll_hit_die(self):
        """
        Rolls a hit die

        :rtype: int
        """
        return self._hit_die.roll()

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

    def feats(self):
        """
        returns the list of available class feats

        :rtype: ClassFeat[]
        """
        feats = list()
        for level in range(0, self.current_level()):
            for class_feat in self._special[level]:
                contains_feat = False
                for feat in feats:
                    if class_feat[0] == feat.name:
                        contains_feat = True
                        feat.level = class_feat[1]
                        break
                if contains_feat is False:
                    feats.append(ClassFeat(class_feat[0]))
        return feats

    def __increase_skill_points(self, character):
        skill_points = (self._skill_modifier + character.intellect_mofifier())
        # only the first class gets the initial skill bonus
        if self._level == 1 and len(character._classes) == 1:
            skill_points *= 4
            if skill_points < 4:
                skill_points = 4
        self._skill_points += skill_points

    def __increase_health(self, character):
        const_mod = character.constitution_mofifier()
        if const_mod < 0:
            const_mod = 0
        hp_bonus = self._hit_die.roll() + const_mod
        character._hit_points["maximum"] += hp_bonus
        character._hit_points["current"] += hp_bonus

    def __repr__(self):
        return "<" + self._name + " Level " + str(self._level) + ">"


class Race(object):

    """
    :type _name: str
    :type _middle_age: int
    :type _old_age: int
    :type _venerable_age: int
    :type _maximum_age: int
    :type _adulthood: int
    :type _starting_age_young: int
    :type _starting_age_medium: int
    :type _starting_age_old: int
    :type _height_modifier_roll: int
    :type _body: dict
    """

    __ALL_RACES = list()

    def __init__(self):
        """
        Creates a Race object
        """
        self._name = None
        self._middle_age = 0
        self._old_age = 0
        self._venerable_age = 0
        self._maximum_age = 0
        self._adulthood = 0
        self._starting_age_young = 0
        self._starting_age_medium = 0
        self._starting_age_old = 0
        self._height_modifier_roll = 0
        self._body = dict()

    def __repr__(self):
        return "<" + self._name + ">"

    @staticmethod
    def load(data_path):
        """
        Loads races from a data file. This method should be called when initializing a package that contains
        game specific race data.

        :param str data_path: The path to the data file in json format, relative to the root package
        """
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
        """
        Returns a race with the given name if one is loaded.

        :param str race_name: The name of the race
        :rtype: Race | None
        """
        for race in Race.__ALL_RACES:
            if race._name.lower() == race_name.lower():
                return copy.deepcopy(race)
        return None

    def height(self, gender):
        """
        Calculate a random height in inch for a character

        :param str gender: The gender of the character. possible values are "male" and "female".
        :rtype: float
        """
        body = self._body[gender]
        modifier_dice = Dice.from_string(body["height_modifier"])
        self._height_modifier_roll = modifier_dice.roll()
        return body["base_height"] + (float(self._height_modifier_roll) / 12)  # calculating in inch

    def weight(self, gender):
        """
        Calculate a random weight in pounds for a character

        :param str gender: The gender of the character. possible values are "male" and "female".
        :rtype: float
        """
        if self._height_modifier_roll is None:
            self.height(gender)
        modifier_dice = Dice.from_string(self._body[gender]["weight_modifier"])
        return self._body[gender]["base_weight"] + (self._height_modifier_roll * modifier_dice.roll())

    def starting_age_dice(self, age_type):
        """
        Returns the dice for rolling the starting age depending on the age type.

        :param str age_type: The age type. Possible values are "young", "medium" and "old"
        :rtype: Dice
        """
        if age_type == "young":
            return self._starting_age_young
        if age_type == "medium":
            return self._starting_age_medium
        if age_type == "old":
            return self._starting_age_old


class Feat(object):

    """
    :type name: str
    :type prerequisites: list
    :type benefit: str
    """

    __ALL_FEATS = list()

    def __init__(self, name=None, prerequisites=list(), benefit=None):
        """
        Creates a Feat object

        :param str name: The name of the feat
        :param str[] prerequisites: Prerequisites of the feat
        :param str benefit: The benefit of the feat
        """
        self.name = name
        self.prerequisites = prerequisites
        self.benefit = benefit

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


class ClassFeat(Feat):

    def __init__(self, name=None, level=1):
        super(ClassFeat, self).__init__(name)
        self.level = level


class Skill(object):

    """
    :type name: str
    :type level: int
    :type ability: str
    :type untrained: bool
    """

    __ALL_SKILLS = list()

    def __init__(self, name=None, level=0, ability=None, untrained=False):
        """
        Creates a Skill instance

        :param str name: The name of the skill
        :param int level: The level of the skill
        :param str ability: The ability of the skill
        :param bool untrained: Whether the skill can be used untrained
        """
        self.name = name
        self.level = level
        self.ability = ability
        self.untrained = untrained

    def __repr__(self):
        return "<" + self.name + " Level " + str(self.level) + ">"

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

    @staticmethod
    def load(data_path):
        """
        Loads skills from a data file. This method should be called when initializing a package that contains
        game specific skill data.

        :param str data_path: The path to the data file in json format, relative to the root package
        """
        data_file = relative_path() + "/" + data_path
        skills = json.loads(open(data_file, encoding="utf-8").read())["skills"]
        Skill.__ALL_SKILLS = list()
        for skill in skills:
            Skill.__ALL_SKILLS.append(Skill(skill["name"], 0, skill["ability"], skill["untrained"]))
