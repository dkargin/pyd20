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

Кейс 1. Два воина: двуручный меч против щит-меч
Кейс 2. Рейнджер против двуручного, charge

Что сделано:

1. Стандартная атака
1. Перемещение
1. Полнораундовая атака замещена стандартным действием
1. Базовые классовые прогрессии: BAB, saving throw, HP



# Ближайший план #

1. Разделить combatant и Character. Character - содержит "лист персонажа". Combatant - упрощёное представление. А оно точно так надо?
1. Одеть персонажей (броня, оружие, щит)
    1. написать список брони, заполнить вручную
    1. добавить AC от брони
1. Полнораундовая атака
1. TWF
1. Атаки по возможности
1. Стили атак:
    1. defensively
    1. power attack
    1. шквал ударов
1. Особые атаки
    1. trip
    1. disarm
1.

Полнораундовая атака: [BAB series]
TWF-1: [BAB series -2] + [Offhand-2]
TWF-2: [BAB series -2] + [Offhand-2] + [Offhand-7]
TWF-3: [BAB series -2] + [Offhand-2] + [Offhand-7]

