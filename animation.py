import math


class Animation(object):
    def __init__(self):
        self._time_start = 0

    def start(self, time):
        self._time_start = time

    def delta_time(self, now):
        return now - self._time_start

    def update(self, time):
        pass

    def is_complete(self, time):
        return True

    def __str__(self):
        return "Animation"

def get_interpolated_coord(path, position):
    max_len = len(path)
    if max_len == 0:
        return

    index_start = math.floor(position)
    index_end = math.ceil(position)

    if index_end > max_len-1:
        tile = path[max_len-1]
        return tile.x, tile.y
    if index_end == 0:
        tile = path[0]
        return tile.x, tile.y

    src = path[index_start]
    t = position - index_start
    dst = path[math.ceil(position)]

    x = src.x + t * (dst.x - src.x)
    y = src.y + t * (dst.y - src.y)
    return x,y


class MovePath(Animation):
    # Shows 'slow' movement from current tile to destination target
    """
    :type _path: grid.Path
    """
    def __init__(self, entity, path, speed = 3.0):
        self._entity = entity
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
        entity = self._entity
        (entity.visual_X, entity.visual_Y) = get_interpolated_coord(self._path, self._position)
        #print("%f of path left" % (self._len - self._position))

    def __repr__(self):
        return "MovePath(%f)" % self._position

class MoveLine(Animation):
    # Shows 'slow' movement from current tile to destination target
    def __init__(self, combatant, target):
        self._combatant = combatant
        self._target = target
        self._position = 0.0

    def __str__(self):
        return "MoveLine(%s)" % self._combatant.get_name()


# Animation for attack start
class AttackStart(Animation):
    def __init__(self, combatant, target):
        self._combatant = combatant
        self._target = target

    def update(self, time):
        pass

    def __str__(self):
        return "AttackStart(%s->%s)" % (self._combatant.get_name(), self._target.get_name())


class AttackFinish(Animation):
    def __init__(self, combatant, target):
        self._combatant = combatant
        self._target = target

    def update(self, time):
        pass

    def __str__(self):
        return "AttackFinish(%s->%s)" % (self._combatant.get_name(), self._target.get_name())
