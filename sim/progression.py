from .character import Progression
from .core import *
from .dice import Dice


# Common class progression
class Basic(Progression):
    def __init__(self, **kwargs):
        super(Basic, self).__init__()
        self.bab_speed = kwargs.get('bab', HIGH)
        self.fort = kwargs.get('fort', LOW)
        self.ref = kwargs.get('ref', LOW)
        self.will = kwargs.get('will', LOW)
        self.hits = kwargs['hits']

    # Calculate bab for specified level
    def calculate_bab(self, level):
        if self.bab_speed == 0:
            return level / 2
        elif self.bab_speed == 1:
            return (level * 3) / 4
        else:
            return level

    def apply(self, ch, level_from, level_to):
        # Calculate saving throw
        def calculate_save(level, flag):
            if flag == HIGH:
                result = int(level / 2)
                if level > 0:
                    result += 2
                return result
            else:
                return int(level / 3)
        # Apply BAB
        ch._BAB += int(self.calculate_bab(level_to) - self.calculate_bab(level_from))
        # Apply saving throw progression
        ch.modify_save_fort(calculate_save(level_to, self.fort) - calculate_save(level_from, self.fort), True)
        ch.modify_save_ref(calculate_save(level_to, self.ref) - calculate_save(level_from, self.ref), True)
        ch.modify_save_will(calculate_save(level_to, self.will) - calculate_save(level_from, self.will), True)
        # Apply hit points progression
        hit_points = ch.constitution_modifier() * (level_to - level_from)
        if ch.current_level() == 0:
            hit_points += self.hits
            level_to -= 1
        dice = Dice()
        for a in range(level_to):
            dice.add_die(self.hits)

        hit_points += dice.roll()
        ch._health_max += hit_points


# Progression that adds stateless feat on specified level
class Feat(Progression):
    def __init__(self, feat, level):
        super(Feat, self).__init__()
        self._feat = feat
        self._level = level

    def apply(self, character, level_from, level_to):
        if self._level in range(level_from, level_to):
            character.add_feat(self._feat)


# Adds feat level progression
class FeatLevel(Progression):
    def __init__(self, feat, levels_upgrade=[], *args, **kwargs):
        self._feat = feat
        self._feat_args = args
        self._feat_kwargs = kwargs
        self._levels = levels_upgrade

    def apply(self, character, level_from, level_to):
        # Check if character has fet
        if not character.get_feat_type(self._feat):
            feat = self._feat(*self._feat_args, **self._feat_kwargs)
            character.add_feat(feat)