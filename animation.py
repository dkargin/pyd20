import math
from sim.entity import *
from sim.grid import Point


# List of active graphical effects
# Renderer iterates through all effects and draws them all
graphic_effects = []


# Contains a set of 'draw' functions
# Renderer sets actual implementation for each drawer/type
class Drawers:
    projectile = None


class GraphicEffect(object):
    """
    Any sort of graphical effects
    """
    def __init__(self, **kwargs):
        self._coord = kwargs.get('coord', Point())
        self._visible = False

    def is_visible(self):
        return self._visible

    def draw(self):
        pass


class Projectile(GraphicEffect):
    def __init__(self, start, target, **kwargs):
        super(Projectile, self).__init__(**kwargs)
        self._ptype = kwargs.get('type')
        self._velocity = kwargs.get('vel')
        self._target = target
        self._start = start
        self._position = 0
        self._visible = True
        # Projectile direction
        self._dir = (self._target - self._start).normalize()

    def coord(self):
        return self._start + self._dir * self._position

    def draw(self):
        if Drawers.projectile is not None:
            Drawers.projectile(self)

    def move(self, time):
        self._position += self._velocity * time
        self._coord = self._start + self._dir * self._position

    def line(self, l=1):
        return (self._coord + self._dir*l).tuple()


class Animation(object):
    """
    Generic animation object
    battle turn generator provides a sequence of animated actions
    """
    def __init__(self, entity: Entity):
        self._time_start = 0
        self._entity = entity

    def on_start(self, time):
        self._time_start = time

    def delta_time(self, now):
        return now - self._time_start

    def update(self, time):
        pass

    def on_stop(self, time):
        pass

    def is_complete(self, time):
        return True

    def __str__(self):
        return "Animation"

    def move_visual(self, coord, change_dir=True):
        deltaX = coord.x - self._entity.visual_X
        deltaY = coord.y - self._entity.visual_Y
        self._entity.visual_X = coord.x
        self._entity.visual_Y = coord.y

        if change_dir:
            if abs(deltaX) >= abs(deltaY):
                self._entity.visual_dir = DIRECTION_RIGHT if deltaX > 0 else DIRECTION_LEFT
            else:
                self._entity.visual_dir = DIRECTION_FRONT if deltaY > 0 else DIRECTION_BACK


def get_interpolated_line(src, dst, t):
    x = src.x + t * (dst.x - src.x)
    y = src.y + t * (dst.y - src.y)
    return Point(x=x, y=y)


def get_interpolated_path_coord(path, position):
    max_len = len(path)
    if max_len == 0:
        return None

    index_start = math.floor(position)
    index_end = math.ceil(position)

    if index_end > max_len-1:
        tile = path[max_len-1]
        return tile
    if index_end == 0:
        tile = path[0]
        return tile

    src = path[index_start]
    t = position - index_start
    dst = path[math.ceil(position)]
    return get_interpolated_line(src, dst, t)


class MovePath(Animation):
    # Shows 'slow' movement from current tile to destination target
    """
    :type _path: grid.Path
    """
    def __init__(self, entity, path, speed = 10.0):
        super(MovePath, self).__init__(entity)
        self._path = path
        self._speed = speed
        self._len = len(path)
        self._position = 0

    def __str__(self):
        return "MovePath(%s)" % self._entity.get_name()

    def position_from_time(self, time):
        return self._speed * self.delta_time(time)

    def is_complete(self, time):
        return self._position >= self._len

    def update(self, time):
        self._position = self.position_from_time(time)
        self.move_visual(get_interpolated_path_coord(self._path, self._position))
        #print("%f of path left" % (self._len - self._position))

    def __repr__(self):
        return "MovePath(%f)" % self._position


class MoveLine(Animation):
    # Shows 'slow' movement from current tile to destination target
    def __init__(self, combatant: Entity, target: Point):
        super(MoveLine, self).__init__(combatant)
        self._target = target
        self._src = combatant.get_coord()
        self._dst = target
        self._position = 0.0

    def is_complete(self, time):
        return self._position >= self._len

    def update(self, time):
        self._position = self.position_from_time(time)
        self.move_visual(get_interpolated_line(self.src, self._dst, self._position))

    def __str__(self):
        return "MoveLine(%s)" % self._combatant.get_name()


# Animation for melee attack
# moves attacker towards target
# Should take about 1sec to complete
class MeleeAttackStart(Animation):
    # Distance that character will advance for attack animation
    ATTACK_MOVE_DISTANCE = 0.5

    def __init__(self, combatant: Entity, target: Entity):
        super(MeleeAttackStart, self).__init__(combatant)
        self._target = target
        self._offset = combatant.get_coord()-combatant.get_center()
        self._src = combatant.get_center()
        self._dst = target.get_center()
        delta = (self._dst - self._src).normalize()
        self._move_target = self._src+ delta * MeleeAttackStart.ATTACK_MOVE_DISTANCE
        self._t = 0
        self._duration = 0.2

    def is_complete(self, time):
        return self.delta_time(time) >= self._duration

    def update(self, time):
        self._t = self.delta_time(time) / self._duration
        coord = get_interpolated_line(self._src, self._move_target, self._t**2)
        self.move_visual(coord + self._offset)

    def __str__(self):
        return "AttackStart(%s->%s)" % (self._entity.get_name(), self._target.get_name())


# Animation for melee attack
# moves attacker towards target
# Should take about 1sec to complete
class RangedAttack(Animation):
    # Distance that character will advance for attack animation
    ATTACK_MOVE_DISTANCE = 0.5

    def __init__(self, combatant: Entity, target: Entity):
        super(RangedAttack, self).__init__(combatant)
        self._target = target
        self._src = combatant.get_center()
        self._dst = target.get_center()
        self._distance = (self._dst - self._src).len()
        self._duration = 2
        self._projectile = Projectile(self._src, self._dst, vel=self._distance/self._duration)

    def is_complete(self, time):
        return self._projectile._position >= self._distance

    def update(self, time):
        self._projectile.move(self.delta_time(time))

    def on_start(self, time):
        self._time_start = time
        graphic_effects.append(self._projectile)

    def on_stop(self, time):
        graphic_effects.remove(self._projectile)

    def __str__(self):
        return "RangedAttack(%s->%s)" % (self._entity.get_name(), self._target.get_name())


# Returns to real position
class MeleeAttackFinish(Animation):
    def __init__(self, combatant, target):
        super(MeleeAttackFinish, self).__init__(combatant)
        self._target = target
        self._src = combatant.get_visual_coord()
        self._dst = combatant.get_coord()
        self._duration = 0.3

    def is_complete(self, time):
        return self.delta_time(time) >= self._duration

    def update(self, time):
        self._t = self.delta_time(time) / self._duration
        coord = get_interpolated_line(self._src, self._dst, self._t)
        self.move_visual(coord, change_dir=False)
        if self.is_complete(time):
            self._entity.fix_visual()

    def __str__(self):
        return "AttackFinish(%s->%s)" % (self._entity.get_name(), self._target.get_name())
