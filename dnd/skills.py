from sim.character import Skill
from sim.core import *
"""
=============================================================================
Skills are here
"""


class SkillTumble(Skill):
    trained = True
    armor = True
    ability = STAT_DEX
    name = "tumble"


class SkillBalance(Skill):
    trained = False
    armor = True
    ability = STAT_DEX
    name = "balance"


class SkillConcentration(Skill):
    trained = False
    armor = False
    ability = STAT_CON
    name = "concentration"


class SkillJump(Skill):
    trained = False
    armor = True
    ability = STAT_STR
    name = "jump"


class SkillSpot(Skill):
    trained = False
    armor = False
    ability = STAT_WIS
    name = "spot"


class SkillSearch(Skill):
    trained = False
    armor = False
    ability = STAT_INT
    name = "search"


class SkillHide(Skill):
    trained = False
    armor = False
    ability = STAT_INT
    name = "hide"


class SkillMoveSilent(Skill):
    trained = False
    armor = False
    ability = STAT_INT
    name = "move_silent"
