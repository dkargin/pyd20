from battle import BattleAction


class WaitAction(BattleAction):
    """
    Implements an action that does nothing
    """

    def __init__(self):
        super(WaitAction, self).__init__()

    def action_point_cost(self):
        return 1

    def execute(self):
        pass


class EndTurnAction(BattleAction):
    """
    Implements the action that ends the turn
    """

    def __init__(self):
        super(EndTurnAction, self).__init__()

    def action_point_cost(self):
        return 0

    def execute(self):
        pass
