Действия

1. Move
2. Standard action: Attack, Spell, ...
3. Full round
4. Charge


Style:
	Power attack
	Fight Defencively
	Combat expertise

Feats:
	- enable style
	- alter damage


# AI #

Сначала прикручиваем такие виды простых мозгов:

- standing warrior. 
- agressive warrior. Move to target + attack
- evasive ranger. Move away + attack
- manual (player). Asks for a move on each turn

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

Что сделано:

1. Basic actions:
    - Standard attack
    - Movement
1. Basic class progression internals: BAB, saving throw, HP
1. Basic weapons, armors and shields and its stats
1. Full round attack + TWF. Though

# Ближайший план #

1. Атаки по возможности
1. Movement speed and armor penalty
1. Animations:
    - movement
    - attack
1. Feats:
    1. Rage
    1. Monk wis to AC

    Flurry of blows
    Rage
    Power attack


# Brain #

Brain update is implemented as generator/coroutine function. It iteratively returns next 'mini-action'. After mini-action is resolved, control returns to generator

