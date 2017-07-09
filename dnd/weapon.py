from battle.item import *

# Simple weapons
dagger = Weapon(name='dagger', damage=d4,
                light=SIZE_SMALL,
                crit_mult=2, crit_range=2,
                range=10)
# Light martial
kukri = Weapon(name='Kukri', damage=d4,
               light=SIZE_MEDIUM,
               crit_mult=2,
               crit_range=3,
               range=0)

kama = Weapon(name='kama', damage=d6,
               light=SIZE_SMALL,
               crit_mult=2,
               crit_range=1,
               range=0)

quarterstaff = Weapon(name='quarterstaff', damage=d6,
              light=SIZE_SMALL,
              crit_mult=2,
              crit_range=1,
              range=0)

shortsword = Weapon(name='Shord sword',
                    damage=d6,
                    light=SIZE_MEDIUM,
                    crit_mult=2, crit_range=2,
                    range=0)
# Medium martial
longsword = Weapon(name='Long sword', damage=d8, light=SIZE_LARGE,
                        crit_mult=2, crit_range=2,
                        range=0)

rapier = Weapon(name='Rapier', damage=d6, light=SIZE_MEDIUM,
                     crit_mult=2, crit_range=3,
                     finesse=True,range=0)

scimitar = Weapon(name='Scimitar', damage=Dice("d6"), light=SIZE_LARGE,
                  crit_mult=2, crit_range=3,
                  range=0)
# two_handed melee
falchion = Weapon(name='Falchion', damage=Dice("2d6"), light=SIZE_HUGE,
                  two_handed=True,
                  crit_mult=2, crit_range=3)

glaive = Weapon(name='Glaive',
                damage=Dice("d10"),
                light=SIZE_HUGE,
                two_handed=True,
                crit_mult=3, crit_range=1,
                reach=Weapon.REACH_UNIVERSAL)

guisarme  = Weapon(name='Guisarme',
                damage=Dice("d10"),
                light=SIZE_HUGE,
                two_handed=True,
                crit_mult=3, crit_range=1,
                reach=Weapon.REACH_UNIVERSAL, trip=True)

halberd = Weapon(name='Halberd', damage=Dice("d10"), light=SIZE_LARGE,
                  two_handed=True,
                  crit_mult=3, crit_range=1, trip=True)

greatsword = Weapon(name='Greatsword',
                    damage=Dice("2d6"),
                    light=SIZE_HUGE,
                    two_handed=True,
                    crit_mult=2, crit_range=1)

scythe = Weapon(name='Scythe',
                    damage=Dice("1d4"),
                    light=SIZE_HUGE,
                    two_handed=True,
                    crit_mult=4, crit_range=1)

