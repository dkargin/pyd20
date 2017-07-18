from sim.item import *

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
               range=0, weight=2)

quarterstaff = Weapon(name='quarterstaff', damage=d6,
              light=SIZE_SMALL,
              crit_mult=2,
              crit_range=1,
              range=0, weight=4)

shortsword = Weapon(name='Shord sword',
                    damage=d6,
                    light=SIZE_MEDIUM,
                    crit_mult=2, crit_range=2,
                    range=0, weight=2)
# Medium martial
longsword = Weapon(name='Long sword', damage=d8, light=SIZE_LARGE,
                        crit_mult=2, crit_range=2,
                        range=0, weight=4)

rapier = Weapon(name='Rapier', damage=d6, light=SIZE_MEDIUM,
                     crit_mult=2, crit_range=3,
                     finesse=True,range=0, weight=2)

scimitar = Weapon(name='Scimitar', damage=Dice("d6"), light=SIZE_LARGE,
                  crit_mult=2, crit_range=3,
                  range=0, weight=4)
# two_handed melee
falchion = Weapon(name='Falchion', damage=Dice("2d6"), light=SIZE_HUGE,
                  two_handed=True,
                  crit_mult=2, crit_range=3, weight=8)

glaive = Weapon(name='Glaive',
                damage=Dice("d10"),
                light=SIZE_HUGE,
                two_handed=True,
                crit_mult=3, crit_range=1,
                reach=Weapon.REACH_UNIVERSAL, weight=10)

guisarme  = Weapon(name='Guisarme',
                damage=Dice("d10"),
                light=SIZE_HUGE,
                two_handed=True,
                crit_mult=3, crit_range=1,
                reach=Weapon.REACH_UNIVERSAL, trip=True, weight=12)

halberd = Weapon(name='Halberd', damage=Dice("d10"), light=SIZE_LARGE,
                  two_handed=True,
                  crit_mult=3, crit_range=1, trip=True, weight=12)

greatsword = Weapon(name='Greatsword',
                    damage=Dice("2d6"),
                    light=SIZE_HUGE,
                    two_handed=True,
                    crit_mult=2, crit_range=2, weight=8)

scythe = Weapon(name='Scythe',
                    damage=Dice("2d4"),
                    light=SIZE_HUGE,
                    two_handed=True,
                    crit_mult=4, crit_range=1, weight=10)
# Exotic
bastard_sword = Weapon(name='bastard sword', damage=d10, light=SIZE_LARGE,
                   crit_mult=2, crit_range=2,
                   range=0, weight=4)

# Simple ranged weapons
crossbow_heavy = Weapon(name='Heavy crossbow',
                 damage=Dice("1d10"),
                 light=SIZE_HUGE, two_handed=True,
                 crit_range=2, crit_mult=2, range=120, reload=ACTION_TYPE_FULL_ROUND, weight=8)

crossbow_light = Weapon(name='Light crossbow',
                       damage=Dice("1d8"),
                       light=SIZE_HUGE, two_handed=True,
                       crit_range=2, crit_mult=2, range=80, reload=ACTION_TYPE_MOVE, weight=4)

# Martial ranged weapons
longbow = Weapon(name='Long bow',
                 damage=Dice("1d8"),
                 light=SIZE_HUGE, two_handed=True,
                 crit_mult=3, range=100)

longbow_composite = Weapon(longbow, name='Composite long bow', range=110)

shortbow = Weapon(name='Short bow',
                 damage=Dice("1d6"),
                 light=SIZE_HUGE, two_handed=True,
                 crit_mult=3, range=60)

shortbow_composite = Weapon(shortbow, name='Composite short bow', range=70)

