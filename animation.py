


class Animation(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def is_complete(self):
        pass


class AnimationMove(Animation):
    # Shows 'slow' movement from current tile to destination target
    def __init__(self, combatant, target):
        self._combatant = combatant
        self._target = target

class AnimationAttack(Animation):
    def __init__(self, combatant, target):
        self._combatant = combatant
        self._target = target
