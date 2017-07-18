# Brain #

Brain update is implemented as generator/coroutine function. It iteratively returns next 'mini-action'. After mini-action is resolved, control returns to generator

I have the following brains implemented:

- aggressive warrior. Moves to target and attacks it. Implemented in class MoveAttackBrain
- standing warrior. No movement is allowed for him. But will attack any target in range. Implemented in class StandAttackBrain

Brains to be implemented:

- evasive ranger. Move away + attack.
- manual (player). Asks for a move on each turn
- planning bitch.

Custom attacks

- Trip. Touch attack + roll contest
    - Stand up
- Disarm
- Sunder

# A way towards smarter brain #

Proposing another brain update loop:

1. Generate possible actions for current turn state:
2. If no actions available - end turn (or planning)
3. Pick best actions and execute
4. GoTo 1

Goal example: survive and ...

# Possible actions #


## Move ##

There are damn many variants for movement. Ideally we should provide here all cells within a reach

## Standard action towards target ##

We should find all adjacent enemies available for this action. We should prune this list by picking most dangerous targets

## Use feat ##

- Use skill

## Run full attack action ##

There can be 5ft step as well. Also there can be

## Spring attack ##

Generally speaking it is damn complex thing for planning, because it consists of two movements

But the second movement can be 'reduced' to 'move to safest place' case


I guess I should implement spells and abilities first before returning to this planning brain


# General thoughts #

1. move;attack1
2. attack1; move
3. (attack1; 5ft; attack2; attack3)
4.
