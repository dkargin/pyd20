#!/usr/bin/python3
# -*- coding: utf-8 -*-
import math

UNIT_LENGTH_FEET = 1.0
UNIT_LENGTH_METER = 0.3048

UNIT_WEIGHT_POUND = 1.0
UNIT_WEIGHT_KILOGRAM = 0.45359237

unit_length = UNIT_LENGTH_FEET
unit_weight = UNIT_WEIGHT_POUND

SIZE_CATEGORIES = {
    "fine": {
        "height": [0, 0.5],
        "width":  [0, 1/8],
        "ac_modifier": 8
    },
    "diminutive": {
        "height": [0.5, 1],
        "width":  [1/8, 1],
        "ac_modifier": 4
    },
    "tiny": {
        "height": [1, 2],
        "width":  [1, 8],
        "ac_modifier": 2
    },
    "small": {
        "height": [2, 4],
        "width":  [8, 60],
        "ac_modifier": 1
    },
    "medium": {
        "height": [4, 8],
        "width":  [60, 500],
        "ac_modifier": 0
    },
    "large": {
        "height": [8, 16],
        "width":  [500, 2000],
        "ac_modifier": -1
    },
    "huge": {
        "height": [16, 32],
        "width":  [2000, 16000],
        "ac_modifier": -2
    },
    "gargantuan": {
        "height": [32, 64],
        "width":  [16000, 125000],
        "ac_modifier": -4
    },
    "colossal": {
        "height": [64, 9999],
        "width":  [125000, 999999999],
        "ac_modifier": -8
    }
}


def ability_modifier(value):
    """
    calculates the ability modifier

    :rtype: int
    """
    if value % 2 != 0:
        value -= 1
    return int((value - 10)/2)


def bonus_spells(value):
    """
    calculates the bonues spells available per ability score

    :rtype: int
    """
    modifier = ability_modifier(value)
    bonus_spells = list()
    level = 0
    while modifier >= level:
        if level == 0:
            bonus_spells.append(0)
            level += 1
            continue
        bonus = (modifier - level + 1) / 4
        bonus = math.ceil(bonus)
        bonus_spells.append(bonus)
        level += 1
    return bonus_spells


def attack_bonus(level, type='good'):
    """
    calculates the attack bonus for a given level and bonus type
    valid type values are: 'good', 'average' and 'poor'

    :rtype: int
    """
    bonus = list()
    base_bonus = 0
    if type == 'good':
        base_bonus = level
    if type == 'average':
        base_bonus = math.ceil(0.75 * level - 0.75)
    if type == 'poor':
        base_bonus = int(level/2)
    bonus.append(base_bonus)
    last_bonus = base_bonus
    while last_bonus > 5:
        last_bonus -= 5
        bonus.append(last_bonus)
    return bonus


def save_bonus(level, type='good'):
    """
    calculates the save bonus for a given level and bonus type
    valid type values are: 'good', and 'poor'

    :rtype: int
    """
    if type == 'good':
        return int(level/2) + 2
    if type == 'poor':
        return int(level/3)
    return 0


def needed_xp(level):
    """
    calculates the xp needed to level up to a specific level

    :rtype: int
    """
    return 500 * math.pow(level, 2) - 500 * level


def level_progress(xp):
    """
    calculates the current level progress

    :rtype: int
    """
    float_level = (1 + math.sqrt(xp / 125 + 1)) / 2
    return float_level - int(float_level)


def current_level(xp):
    """
    calculates the level for the current xp

    :rtype: int
    """
    return int((1 + math.sqrt(xp / 125 + 1)) / 2)


def class_skill_max_ranks(level):
    """
    calculates the max ranks in a class skill

    :rtype: int
    """
    return level + 3


def cross_class_skill_max_ranks(level):
    """
    calculates the max ranks in a cross class skill

    :rtype: int
    """
    return (level + 3) / 2


def new_feat_available(level):
    """
    returns True if a new feat is available on the given level

    :rtype: bool
    """
    if level == 1:
        return True
    return level % 3 == 0


def increase_ability_scores(level):
    """
    returns True if the ability scores may be increased

    :rtype: bool
    """
    return level % 4 == 0


def size_category(height):
    """
    returns the size category for the specified height in feet

    :param float height: The height
    :return: str
    """
    result_category = None
    for category in SIZE_CATEGORIES:
        min_height = SIZE_CATEGORIES[category]["height"][0]
        if(height > min_height):
            result_category = category
    return result_category


def ac_size_modifier(height):
    """
    calculates the armor class size modifier for the specified height

    :param float height: The height in feet
    :return: int
    """
    return SIZE_CATEGORIES[size_category(height)]["ac_modifier"]
