import pygame
from sim.grid import *
import pygame.transform as transform
from sim.entity import *

# Maps item name to icon path
item_sprites = {
    'longsword' : '',
    'bastard_sword' : '',
    'composite_bow' : '',
}


class SpriteSheet:
    def __init__(self, size, path):
        self._size = size
        self.surface = pygame.image.load(path)
        self.tx = self.surface.get_width() / size
        self.ty = self.surface.get_height() / size

    # Returns rect for picked tile
    def get_rect(self, x, y):
        return x*self._size, y*self._size, self._size, self._size

    # Returns tile subsurface
    def subsurface(self, x, y):
        return self.surface.subsurface(self.get_rect(x,y))


# Model description
class ModelSet:
    def __init__(self, mon_size, **kwargs):
        """

        :param mon_size: - monster size
        :param front: - a set of 'front' tiles
        :param back: - a set of 'back' tiles
        :param side:
        """
        self.size = mon_size
        # List of front frames
        self.front = kwargs.get('front', [])
        # List of back frames
        self.back = kwargs.get('back', [])
        # List of left frames
        self.left = kwargs.get('left', [])
        # List of right frames
        self.right = kwargs.get('right', [])
        self.ground_up = kwargs.get('ground_up', [])
        self.ground_down = kwargs.get('ground_down', [])

    def generate_size(self, size):
        if size == self.size:
            return self

        result = ModelSet(size)

        for surf in self.front:
            result.front.append(transform.scale2x(surf))

        for surf in self.back:
            result.back.append(transform.scale2x(surf))

        for surf in self.left:
            result.left.append(transform.scale2x(surf))

        for surf in self.right:
            result.right.append(transform.scale2x(surf))

        for surf in self.ground_up:
            result.ground_up.append(transform.scale2x(surf))

        for surf in self.ground_down:
            result.ground_down.append(transform.scale2x(surf))

        return result


"""
Spritesheet contains a set of frames for 'front', 'back' and 'right' positions
I should flip 'right' to obtain 'left' frame set. Also I should get 'prone' frame set by rotating 'right'

I will get rid of this stuff when I reimplement rendering using PyOpenGL.

Config
int row, int front, int back, int right
"""

class ModelDrawer:
    def __init__(self, size, path, mdesc):
        self._sprite_sheet = SpriteSheet(size, path)
        """
        :param size: - tile size
        :param path: - path to tileset image
        """
        self._models = {}
        for name, desc in mdesc.items():
            sprite_set = self._generate_model(desc)
            self._models[name] = {1:sprite_set}

    def _generate_model(self, desc):
        (row, src_front, src_back, src_right) = desc
        model = ModelSet(1)
        # 1. Copy front tiles
        for column in src_front:
            model.front.append(self._sprite_sheet.subsurface(column, row))

        for column in src_back:
            model.back.append(self._sprite_sheet.subsurface(column, row))

        for column in src_right:
            ss = self._sprite_sheet.subsurface(column, row)
            model.right.append(ss)
            left = transform.flip(ss, True, False)
            model.left.append(left)
            down = transform.rotate(ss, 90)
            model.ground_down.append(down)
            up = transform.rotate(ss, -90)
            model.ground_up.append(up)

        return model

    def get_combatant_sprite(self, combatant):
        mtype = combatant.model

        if mtype not in self._models:
            mtype = 'naked'

        models = self._models[mtype]
        model = None

        # Get sprite set acoording to entity size
        monsize = combatant.get_size()

        if monsize not in models:
            base = models[1]
            model = base.generate_size(monsize)
            models[monsize] = model
        else:
            model = models[monsize]

        surface = model.front[0]

        try:
            if not combatant.is_consciousness():
                surface = model.ground_up[0]
            elif combatant.is_prone():
                surface = model.ground_down[0]
            elif combatant.visual_dir == DIRECTION_LEFT:
                surface = model.left[0]
            elif combatant.visual_dir == DIRECTION_RIGHT:
                surface = model.right[0]
            elif combatant.visual_dir == DIRECTION_FRONT:
                surface = model.front[0]
            elif combatant.visual_dir == DIRECTION_BACK:
                surface = model.back[0]
        except:
            pass

        return surface


