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

STATUS_LAST = 0


def new_status():
    global STATUS_LAST
    STATUS_LAST += 1
    result = STATUS_LAST
    return result

# Some boolean statuses that character can have
STATUS_PRONE = new_status()
STATUS_HEAVY_ARMOR = new_status()
STATUS_IGNORE_ARMOR_MOVE = new_status()
STATUS_PARALYZED = new_status()
STATUS_BLIND = new_status()        # Should it have simple status, or complex effect?
STATUS_STUNNED = new_status()
STATUS_FLATFOOTED = new_status()

# Some feats
STATUS_HAS_IMPROVED_TRIP = new_status()
STATUS_HAS_IMPROVED_DISARM = new_status()
STATUS_HAS_IMPROVED_SUNDER = new_status()
STATUS_HAS_IMPROVED_GRAPPLE = new_status()
STATUS_HAS_IMPROVED_UNARMED = new_status()

ITEM_SLOT_ARMOR = 0
ITEM_SLOT_MAIN = 1
ITEM_SLOT_OFFHAND = 2
ITEM_SLOT_HEAD = 3
ITEM_SLOT_FEET = 4

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


class SizeDesc:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.ac_mod = kwargs['ac_mod']
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.tiles = kwargs['tiles']

SIZE_TINY = 2
SIZE_SMALL = 3
SIZE_MEDIUM = 4
SIZE_LARGE = 5
SIZE_HUGE = 6
SIZE_GARGANTUAN = 6

SIZE_CATEGORIES = [
    SizeDesc(name='fine',       tiles=1, height=[0, 0.5], width=[0, 1/8], ac_mod=8),
    SizeDesc(name='diminutive', tiles=1, height=[0.5, 1], width=[1/8, 1], ac_mod=4),
    SizeDesc(name='tiny',       tiles=1, height=[1, 2],   width=[1, 8], ac_mod=2),
    SizeDesc(name='small',      tiles=1, height=[2, 4],   width=[8, 60], ac_mod=1),
    SizeDesc(name='medium',     tiles=1, height=[4, 8], width=[60, 500], ac_mod=0),
    SizeDesc(name='large',      tiles=2, height=[8, 16], width=[500, 2000], ac_mod=-1),
    SizeDesc(name='huge',       tiles=3, height=[16, 32], width=[2000, 16000], ac_mod=-2),
    SizeDesc(name='gargantuan', tiles=4, height=[32, 64], width=[16000, 125000], ac_mod=-4),
    SizeDesc(name='colossal',   tiles=5, height=[64, 9999], width=[125000, 999999999], ac_mod=-8),
]

ACTION_TYPE_LAST = 0


def gen_action_type():
    global ACTION_TYPE_LAST
    result = ACTION_TYPE_LAST
    ACTION_TYPE_LAST += 1
    return result

# Action durations
ACTION_TYPE_STANDARD = gen_action_type()            # Generic standard action
ACTION_TYPE_MOVE = gen_action_type()                # Move action, when combatant actually changes its position
ACTION_TYPE_MOVE_LIKE = gen_action_type()           # Action in place of move action, without actual movement
ACTION_TYPE_FULL_ROUND = gen_action_type()          # Generic full round action
ACTION_TYPE_FULL_ROUND_ATTACK = gen_action_type()   # Full round attack
ACTION_TYPE_FREE = gen_action_type()
ACTION_TYPE_SWIFT = gen_action_type()
# Expends attack action slot. Can be standard action,
# one of full round attacks, or one of attacks of opportunity
ACTION_TYPE_ATTACK = gen_action_type()
ACTION_TYPE_NONE = 6


GENDER_NONE = 0
GENDER_FEMALE = 1
GENDER_MALE = 2


def roll_hits(base, roll, dc):
    if roll == 1:
        return False
    if roll == 20:
        return True
    return base + roll >= dc

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
