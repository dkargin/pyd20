from unittest import TestCase

from battle.grid import Grid, PathFinder, OccupationTemplate


class TestGrid(TestCase):

    def test_create_with_dimension(self):
        grid = Grid(3, 3)
        assert len(grid.get_tiles()) == 9

    def test_path_between_tiles(self):
        grid = Grid(5, 5)
        start = grid.get_tile(1, 1)
        end = grid.get_tile(3, 3)
        pf = PathFinder(grid)
        path = pf.path_between_tiles(start, end)
        assert path is not None
        assert path.length() > 0

    def test_occupation_template(self):
        template1_1 = OccupationTemplate(1, 1)
        print(str(template1_1))
        template1_2 = OccupationTemplate(1, 1, True)
        print(str(template1_2))
        template1_3 = OccupationTemplate(1, 1, True, False)
        print(str(template1_3))

        template2_1 = OccupationTemplate(2, 1)
        template2_2 = OccupationTemplate(2, 1, True)
        template2_3 = OccupationTemplate(2, 1, True, False)

        print(str(template2_1))
        print(str(template2_2))
        print(str(template2_3))

