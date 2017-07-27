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
    - Full attack
1. Basic class progression internals: BAB, saving throw, HP
1. Basic weapons, armors and shields and its stats
1. Pathfinding works for single-tiled creatures (medium and smaller)
1. Basic AI. AI looks for target, moves in weapon range and attacks it
1. Resolving attack of opportunity for movement in threatened area
1. Supported creatures with large and large sizes and appropriate reach
1. Implemented event system to allow feats override different parts of game mechanics. Allows to implement feats in a less intrusive way. More stuff can be implemented without **if character.has_feat('another_feat')** all over the code
1. Core classes
    - Monk. Implemented basic progression and some class feats
    - Fighter. Implemented basic progression
1. Some actions and interactions are animated:
    - movement
    - attack start
    - attack finish


# Plan #

1. Charge attack
    - draw a line
    - move a line
    - can be interrupted!
1. Ranged attack
    - move to range             OK?
    - bow them all              OK?
    - draw an arrow
    - reload action
    - crossbow reload
1. Some skill checks: tumble, spot, search
1. Manual brain
1. Draw weapon sprites
1. Spring attack series. Because they are awesome!
1. Brain should switch weapons according to situation and distance to enemy
1. Vision stuff.
    - Hide, Spot, listen
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
