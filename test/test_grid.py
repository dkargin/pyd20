from unittest import TestCase
from grid import Grid

__author__ = 'Philipp'


class TestGrid(TestCase):

    def test_create_with_dimension(self):
        grid = Grid.create_with_dimension(3, 3)
        assert len(grid.get_tiles()) == 9

    def test_path_between_tiles(self):
        grid = Grid.create_with_dimension(3, 3)
        start = grid.get_tile(1, 1)
        end = grid.get_tile(3, 3)
        path = grid.path_between_tiles(start, end)
        assert path is not None
        assert path.length() > 0
