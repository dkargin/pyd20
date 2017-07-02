import math

UNIT_LENGTH_FEET = 1.0
UNIT_LENGTH_METER = 0.3048

UNIT_WEIGHT_POUND = 1.0
UNIT_WEIGHT_KILOGRAM = 0.45359237

unit_length = UNIT_LENGTH_FEET
unit_weight = UNIT_WEIGHT_POUND

LOW = 0
MEDIUM = 1
HIGH = 2


# Some boolean statuses that character can have
STATUS_PRONE = 1
STATUS_HEAVY_ARMOR = 2
STATUS_IGNORE_ARMOR_MOVE = 3
STATUS_PARALYZED = 4
STATUS_BLIND = 5        # Should it have simple status, or complex effect?
STATUS_STUNNED = 6
STATUS_FLATFOOTED = 7


ITEM_SLOT_ARMOR = 0
ITEM_SLOT_MAIN = 1
ITEM_SLOT_OFFHAND = 2
ITEM_SLOT_HEAD = 3
ITEM_SLOT_FEET = 4

ARMOR_TYPE_NONE = 0
ARMOR_TYPE_LIGHT = 1
ARMOR_TYPE_MEDIUM = 2
ARMOR_TYPE_HEAVY = 3

SIZE_TINY = 1
SIZE_SMALL = 2
SIZE_MEDIUM = 3
SIZE_LARGE = 4
SIZE_HUGE = 5

# Stat indexes
STAT_STR = 0
STAT_DEX = 1
STAT_CON = 2
STAT_INT = 3
STAT_WIS = 4
STAT_CHA = 5

ALIGNMENT_GOOD = "Good"
ALIGNMENT_NEUTRAL = "Neutral"
ALIGNMENT_EVIL = "Evil"
ALIGNMENT_CHAOTIC = "Chaotic"
ALIGNMENT_LAWFUL = "Lawful"

GENDER_MALE = "male"
GENDER_FEMALE = "female"


SIZE_CATEGORIES = [
    {
        "name": "fine",
        "height": [0, 0.5],
        "width":  [0, 1/8],
        "ac_modifier": 8
    },
    {
        "name": "diminutive",
        "height": [0.5, 1],
        "width":  [1/8, 1],
        "ac_modifier": 4
    },
    {
        "name": "tiny",
        "height": [1, 2],
        "width":  [1, 8],
        "ac_modifier": 2
    },
    {
        "name": "small",
        "height": [2, 4],
        "width":  [8, 60],
        "ac_modifier": 1
    },
    {
        "name": "medium",
        "height": [4, 8],
        "width":  [60, 500],
        "ac_modifier": 0
    },
    {
        "name": "large",
        "height": [8, 16],
        "width":  [500, 2000],
        "ac_modifier": -1
    },
    {
        "name": "huge",
        "height": [16, 32],
        "width":  [2000, 16000],
        "ac_modifier": -2
    },
    {
        "name": "gargantuan",
        "height": [32, 64],
        "width":  [16000, 125000],
        "ac_modifier": -4
    },
    {
        "name": "colossal",
        "height": [64, 9999],
        "width":  [125000, 999999999],
        "ac_modifier": -8
    }
]


# Action durations
DURATION_STANDARD = 0
DURATION_MOVE = 1
DURATION_FULLROUND = 2
DURATION_FREE = 3
DURATION_SWIFT = 4


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
        min_height = category["height"][0]
        if height > min_height:
            result_category = category
    return result_category


def ac_size_modifier(height):
    """
    calculates the armor class size modifier for the specified height

    :param float height: The height in feet
    :return: int
    """
    return size_category(height)["ac_modifier"]
