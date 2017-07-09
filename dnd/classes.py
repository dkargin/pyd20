from battle.character import *
import dnd.feats

Fighter = CharacterClass("fighter", [
    ProgressionBAB(HIGH),
    ProgressionHP(10),
    ProgressionSaveThrow(HIGH, LOW, LOW)])

Monk = CharacterClass("monk", [
    ProgressionBAB(HIGH),
    ProgressionHP(8),
    ProgressionSaveThrow(HIGH, HIGH, HIGH),
    ProgressionFeat(dnd.feats.MonkBonusAC(), 1)])

Rogue = CharacterClass("rogue", [
    ProgressionBAB(MEDIUM),
    ProgressionHP(6),
    ProgressionSaveThrow(HIGH, LOW, LOW)])