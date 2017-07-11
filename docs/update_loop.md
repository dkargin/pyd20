# Game update loop #

Update loop consists of :
- battle update loop
- nested combatant update loop

Battle update loop picks another combatant and passes control to event generator from combatant


## Combatant update loop ##

Each character is updated according to its initiative position

- combatant.on_turn_start()

    - deactivate styles from previous turns
    - reset BAB attacks, AoOs and TurnState
    - call character events on_turn_start
    - calculate BAB attacks
        - and run on_calc_attack

- combatant.brain.make_turn()

- combatant.on_turn_end()
    - run character events on_turn_end

## Battle update loop ##

Battle used generator-based approach. It has infinite loop, that picks every character and yields all update events from picked character
