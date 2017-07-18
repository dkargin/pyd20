from sim.character import *
import dnd.feats
import sim.progression as P

Fighter = CharacterClass("fighter", P.Basic(bab=HIGH, hits=10, fort=HIGH, ref=LOW, will=LOW))

Monk = CharacterClass("monk", P.Basic(bab=MEDIUM, hits=8, fort=HIGH, ref=HIGH, will=HIGH),
                      P.Feat(dnd.feats.MonkBonusAC(), 1),
                      P.Feat(dnd.feats.FlurryOfBlows(), 1),
                      P.Feat(dnd.feats.MonkMovement(), 1))

Rogue = CharacterClass("rogue", P.Basic(bab=MEDIUM, hits=6, fort=LOW, ref=HIGH, will=LOW))
