from character import *

Fighter = CharacterClass("Fighter", [
    ProgressionBAB(HIGH),
    ProgressionHP(10),
    ProgressionSaveThrow(HIGH, LOW, LOW)])

Monk = CharacterClass("Monk", [
    ProgressionBAB(HIGH),
    ProgressionHP(10),
    ProgressionSaveThrow(HIGH, LOW, LOW)])