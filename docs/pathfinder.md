# Pathfinder #

Pathfinder uses distance transform to simplify the search

Each combatant uses its own pathfinder

Creature sizes:

| Creature size | Mode
| ---------- | ---------------------------------------- |
|    1 tile  | Regular pathfinding                      |
|    2 tiles | Grow obstacle map for creatures of size 1 and larger |
|    3 tiles | Use distance transform? |
|    4 tiles | Size3 + grow obstacle map |

# Current tasks #

TODO:
    - proper path cost
    - check creature size
    - move to firing range
    - move away from target
    - move pathfinding to brain