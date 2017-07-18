
class BattleEvent(object):
    """
    Basic class for battle events
    """
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class TurnEnd(BattleEvent):
    def __init__(self, combatant):
        super(TurnEnd, self).__init__("turn end")
        self.combatant = combatant


class RoundEnd(BattleEvent):
    def __init__(self, round):
        super(RoundEnd, self).__init__("round end")
        self.round = round


class AnimationEvent(BattleEvent):
    """
    This event contains animation for game action to be shown
    """
    def __init__(self, animation):
        super(AnimationEvent, self).__init__("animation")
        self.animation = animation