# What is this #

This is D&D 3.5 battle ground, implemented in python

# Installation #

p20dnd requires pygame to render battlescape

```
pip install pygame
```

# How to use #

Look at main.py.

1. Create battle instance
1. Generate characters and add them to battle:
1. Keep iterating turns until battle is resolved

# What is implemented #

1. Basic actions:
    - Standard attack
    - Movement
1. Basic class progression internals: BAB, saving throw, HP
1. Basic weapons, armors and shields and its stats
1. Full round attack + TWF
1. Resolving attack of opportunity for movement in threatened area
1. Supported creatures with large and large sizes and reaches
1. Pathfinding works for single-tiled creatures (medium and smaller)
1. Brain picks proper melee attack tile
1. Game loop properly generates animations for combatant actions
1. Core classes
    - Monk. Implemented basic progression and some class feats
    - Fighter. Implemented basic progression
1. Implemented simplistic rendering and animations:
    - smooth movement
    - attack start
    - attack finish


# Plan #

1. Charge attack
    - draw a line
    - move a line
    - can be interrupted!
1. Ranged attack
    - move to range
    - bow them all
    - reload action
    - crossbow reload
1. Status effects and ways to toggle them
1. Simple feats:
    - Monk AC bonus                     OK
    - Weapon finesse                    OK
    - Weapon focus                      OK
    - Improved critical (doubles crit range)
    - Power critical (+4 to crit confirm)   OK
    - Combat reflexes                   OK
    - Deft opportunist                  OK
    - Insightfull strike                OK
    - Defensive Sweep: If an opponent starts their turn adjacent to you and doesn’t move this round, they provoke an AoO at the end of the turn. PHBII pg 78.
    - Quick Staff. Or monk is boring
    - Improved trip
    - Improved disarm
1. Feats providing additional attacks:
    - Two weapon fighting       OK
    - Bow feat series
    - Spinning Halberd
    - Cleave
1. Feats with unique progression (Sneak attack, Flurry of blows, Barbarian Rage)
    - Sneak attack
    - Skirmish
1. Feats that provide 'combat styles'
    - Flurry of blows
    - Power attack
    - Combat expertise
1. Items can lay on ground and can be picked
1. Vision stuff
1. Some spells (most interesting for me):
    - True strike. Remove bonus after the first strike
    - Shield
    - Smite
    - Mage armor
    - Scorching ray
    - Greater invisibility
    - Darkness
    - Grease (skills need to be implemented)
    - Rhino's rush. Need charge to be implemented
    - Fireball
1. Brain should change weapons according to target range and estimated arrival to melee range
1. Test splitting targets during full attack action
    - and use 5ft step as well. Especially for dervish
1. Invisibility
    - brain should know how to deal with it
1. More threat estimation for AI
1. Monster template



