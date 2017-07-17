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