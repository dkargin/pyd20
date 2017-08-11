import copy
import json
import os

from .dice import *
from .core import *


class Race(object):
    """
    Race description
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
    :type _size: int Creature size
    """

    __ALL_RACES = dict()

    def __init__(self, name, **kwargs):
        """
        Creates a Race object
        """
        self._name = name
        self._middle_age = 30
        self._old_age = 50
        self._venerable_age = 75
        self._maximum_age = 100
        self._adulthood = 15
        self._starting_age_young = 10
        self._starting_age_medium = 25
        self._starting_age_old = 60
        self._height_modifier_roll = 0
        # Body variants for male and female
        self._body = dict()
        # Stat adjustments
        self._stats = kwargs.get('stats', [0, 0, 0, 0, 0, 0])
        # Bonuses from race. Implemented as array of feat names
        self._racial_feats = []
        self._size = SIZE_MEDIUM

        Race.__ALL_RACES[self._name] = self

    def __repr__(self):
        return "<" + self._name + ">"

    @property
    def name(self):
        return self._name

    @staticmethod
    def load(data_path):
        """
        Loads races from a data file. This method should be called when initializing a package that contains
        game specific race data.

        :param str data_path: The path to the data file in json format, relative to the root package
        """
        data_file = relative_path() + "/" + data_path
        races = json.loads(open(data_file, encoding="utf-8").read())["races"]
        Race.__ALL_RACES = dict()
        for race in races:
            instance = Race(race["name"])
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
            instance._size = race.get("size", SIZE_MEDIUM)
            instance._stats = race.get("stats", [0, 0, 0, 0, 0, 0])

    @staticmethod
    def with_name(race_name):
        """
        Returns a race with the given name if one is loaded.

        :param str race_name: The name of the race
        :rtype: Race | None
        """
        for name, race in Race.__ALL_RACES.items():
            if name.lower() == race_name.lower():
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
