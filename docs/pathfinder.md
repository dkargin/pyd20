# Pathfinder #

Pathfinder uses distance transform to simplify the search

Each combatant uses its own pathfinder

Creature sizes:

-------------------------------------------------------
    1 tile  | Regular pathfinding
-------------------------------------------------------
    2 tiles |  Grow obstacle map for creatures of size 1 and larger
------------------------------------------------------
    3 tiles | Use distance transform?

# Current tasks #

TODO:
    - proper path cost
    - check creature size
    - move to firing range
    - move away from target
    - move pathfinding to brain