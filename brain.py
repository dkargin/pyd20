import math

class Brain(object):
    def __init__(self):
        self.slave = None
        # Attack target
        self.target = None
        # Path to follow
        self.path = None

    # To be overriden
    def make_turn(self, battle):
        return []


# Object is controlled by keyboard input
class ManualBrain(Brain):
    def __init__(self):
        Brain.__init__(self)
        pass

# Brain for simple movement and attacking
class MoveAttackBrain(Brain):
    def __init__(self):
        Brain.__init__(self)

    def make_turn(self, battle):
        if self.target is None:
            print("Has no target. Finding")
            self.target = battle.find_enemy(self.slave)

        if self.target is None:
            return []

        if battle.is_adjacent(self.slave, self.target):
            print("Target is near, can attack")
        else:
            src =
            path = battle.pathfinder.path_between_tiles(src, dst)
            print("Target %d is away" % self.target.get_name())


        '''
        1. If no enemy - find it
        2. If enemy is in range - full round attack
        2. If enemy is near 5ft - move and full round
        If enemy is far - move to it
        3. If enemy is near for charge - do it
        4.
        :param battlefield:
        :return:
        '''
        return []

