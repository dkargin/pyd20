# AI #

We have the following brains implemented:

- aggressive warrior. Moves to target and attacks it. Implemented in class MoveAttackBrain
- standing warrior. No movement is allowed for him. But will attack any target in range. Implemented in class StandAttackBrain

To be implemented:

- evasive ranger. Move away + attack.
- manual (player). Asks for a move on each turn
- planning bitch.


Все являются наследниками класса Brain

# UI #

Нужны следующие фреймы:
- Battlescape
- Character editor/sheet

## Battlescape ##

1. Рисуем положение участников. OK
2. Последовательность действий
3. Пауза/продолжение
4. Панель с логом сообщений (кто кого во что). Пишу в обычный лог

## Character editor/sheet ##

1.
2. Статус выбраных участников (Character sheet)
3. 

What is done:

1. Basic actions:
    - Standard attack
    - Movement
1. Basic class progression internals: BAB, saving throw, HP
1. Basic weapons, armors and shields and its stats
1. Full round attack + TWF
1. Resolving attack of opportunity for movement in threatened area
1. Pathfinding works
1. Brain picks proper melee attack tile
1. Game loop properly generates animations for combatant actions


# Plan #

1. Movement speed and armor penalty
1. Feats:
    1. Rage
    1. Monk wis to AC
    1. Flurry of blows
    1. Rage
    1. Power attack


# Brain #

Brain update is implemented as generator/coroutine function. It iteratively returns next 'mini-action'. After mini-action is resolved, control returns to generator

