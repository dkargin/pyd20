from sim.character import *
import dnd.feats
import sim.progression as P

def base(**kwargs):
    return P.Basic(**kwargs), P.Feat(dnd.feats.BasicCombat(), 1)

Fighter = CharacterClass("fighter", *base(bab=HIGH, hits=10, fort=HIGH, ref=LOW, will=LOW))

Monk = CharacterClass("monk", *base(bab=MEDIUM, hits=8, fort=HIGH, ref=HIGH, will=HIGH),
                      P.Feat(dnd.feats.MonkBonusAC(), 1),
                      P.Feat(dnd.feats.FlurryOfBlows(), 1),
                      P.Feat(dnd.feats.MonkMovement(), 1))

Rogue = CharacterClass("rogue", *base(bab=MEDIUM, hits=6, fort=LOW, ref=HIGH, will=LOW))

Barbarian = CharacterClass("barbarian", *base(bab=HIGH, hits=12, fort=HIGH, ref=LOW, will=LOW),
                           P.Feat(dnd.feats.Rage('barbarian'), 1))

Warblade = CharacterClass("warblade", *base(bab=HIGH, hits=12, fort=HIGH, ref=LOW, will=LOW),
                           )
