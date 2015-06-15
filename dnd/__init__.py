#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyd20.character import *

Class.load("dnd/classes.json")
Skill.load("dnd/skills.json")
Race.load("dnd/races.json")
Feat.load("dnd/feats.json")

# Classes
Barbarian = Class.with_name('barbarian')
Bard = Class.with_name('bard')
Druid = Class.with_name('druid')
Cleric = Class.with_name('cleric')

# Races
Human = Race.with_name('human')
Dwarf = Race.with_name('dwarf')
Elf = Race.with_name('elf')
Gnome = Race.with_name('gnome')
HalfElf = Race.with_name('half-elf')
HalfOrc = Race.with_name('half-orc')
Halfling = Race.with_name('halfling')
