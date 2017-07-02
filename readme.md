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
1. Core classes
    - Monk. Implemented basic progression and some class feats
    - Fighter. Implemented basic progression


# Plan #

1. Movement speed and armor penalty
1. Charge attack
1. Fighting defencively (and skill bonuses)
1. Feats:
    - Rage
    - Monk AC bonus             OK
    - Flurry of blows
    - Power attack
    - Weapon finisse
    - Weapon focus
    - Power critical
    - Combat reflexes           OK
    - Deft opportunist          OK
    - Insightfull strike
    - Sneak attack
    - Cleave
    - Spinning Halberd
    - Defensive Sweep: If an opponent starts their turn adjacent to you and doesn’t move this round, they provoke an AoO at the end of the turn. PHBII pg 78.
    - Quick Staff. Or monk is boring
    - Improved trip
    - Improved disarm
1. Ranged attack
1. Items can lay on ground
1. Some spells (most interesting for me):
    - True strike. Remove bonus after the first strike
    - Shield
    - Mage armor
    - Scorching ray
    - Greater invisibility
    - Darkness
    - Grease (skills need to be implemented)
    - Rhino's rush. Need charge to be implemented
    - Fireball
1. Brain can change weapons
1. Animation for attack and receiving damage. There could be multiple animation effects
1. Test splitting targets during full attack action
    - and use 5ft step as well

# Brain #

Brain update is implemented as generator/coroutine function. It iteratively returns next 'mini-action'. After mini-action is resolved, control returns to generator

