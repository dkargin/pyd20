from unittest import TestCase
import dice


class DiceTest(TestCase):
    def test_dice(self):
        dice1 = dice.Dice("2d6")
        print("Dice1=%s"%dice1.to_string())
        dice2 = dice.Dice("3d6")
        print("Dice2=%s"%dice2.to_string())
        dice3 = dice.Dice("1d8")
        print("Dice3=%s"%dice3.to_string())

        dice_sum1 = dice1+dice2
        print("sum1=%s"%dice_sum1.to_string())
        dice_sum2 = dice_sum1 + dice3
        print("sum2=%s"%dice_sum2.to_string())
