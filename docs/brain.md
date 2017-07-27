# Brain #

Brain update is implemented as generator/coroutine function. It iteratively returns next 'mini-action'. After mini-action is resolved, control returns to generator

I have the following brains implemented:

- aggressive warrior. Moves to target and attacks it. Implemented in class MoveAttackBrain
- standing warrior. No movement is allowed for him. But will attack any target in range. Implemented in class StandAttackBrain

Brains to be implemented:

- evasive ranger. Move away + attack.
- manual (player). Asks for a move on each turn
- planning bitch.

# Actions #

I've already implemented FSM for basic move/standard/attack/full attack actions.
Brain just iterates over available actions and performs them.

Some custom attacks:

- Trip. Done. It is just a single attack and brain just checks if it is good chance to trip
- Disarm. Need mechanics to pick and switch the weapons
- Sunder. Need mechanics to switch weapons. Everything else is quite simple

## Rush ##

This action is complex one. Rush consists of double movement and attack sequence. Pounce allows to make full attack action.
Rush implementation should consider giving brain a thought after each subaction:
- moved and interrupted. Brain can spend move action after this.
- reached target and made attack. Can brain switch to another target within reach, like it is allowed for full attack actions?
- killed target, got cleave attack. Brain should direct it

State machine:
1. ACTION_CHARGE_MOVE. Yep, create additional action, it gives +move_speed*2
Leads to:
STATE_INITIAL - if something went wrong.
STATE_INITIAL - if have only one attack - make it and end charge
STATE_CHARGE_FULLATTACK. Special state for those, who have 'pounce'
2.

## Spring attack ##

This action is complex one. Consists of:

- move to target
- attack target
- move somewhere

Brain should check


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

# Safe/Danger estimation #

Each combatant/brain should estimate dangerous and safe positions and do pathfinding according to this danger map


# General thoughts #

Brain should think of:

1. Disable a target
1. Damaging the target is also a way of disabling it
1. Stay alive (if not suicider)

Should brain try to analyse some feats and tricks to know it proper effects?

