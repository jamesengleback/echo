import random
from string import ascii_uppercase
import numpy as np
import pandas as pd

class Cpd:
    def __init__(self, name = None, vol = None, parent = None):
        self.uid = ''.join(random.choices(ascii_uppercase, k=8))  # useless?
        self.name = name 
        self.vol = vol
        self.children = []
    def allocate(self, well):
        self.src_wells.append(well)
    def sample(self, vol):
        if vol < self.vol:
            self.vol -= vol
            sample = Cpd(name = self.name, vol = vol, parent = self)
            self.children.append(sample)
            return sample
        else:
            raise OverDrawnException(f'Cpd {self.name} overdrawn available: {self.vol} requested: {vol}')
        # todo - xfer method
    def xfer(self, dest, vol):
        # handle well id
        pass

class Well:
    def __init__(self, contents = None, vol = 0, plateid = None, loc = None, ldv = True):
        self.ldv = ldv
        if self.ldv:
            self.minvol = 2.5
            self.maxvol = 12
        else:
            self.minvol = 15
            self.maxvol = 65
        #self.cpd = cpd # todo - mixture  flexibility for dest plates
        self.plateid = plateid
        self.loc = loc
        self.uid = ''.join(random.choices(ascii_uppercase, k=8))

    @property
    def vol(self):
        return self.cpd.vol
    def fill(self, cpd, vol):
        if cpd.vol > self.maxvol:
            raise OverFillException(f'requested fill vol: {vol} \t max vol: {self.maxvol}')
        if cpd.vol < self.minvol:
            raise UnderFillWarning(f'Well: {self.loc} fill - compound: {cpd.name} - {cpd.vol} < min vol ({self.minvol})')
        self.cpd = cpd.sample(vol) # weak - can be overwritten, only handles 1 compount
    def xfer(self, dest_plate, dest_loc, vol):
        # todo future: mutiple compounds - div vol equally, mixture class?
        # register transfer in objects
        # return dict? -> dataFrame
        dest_plate.wells[dest_loc].fill(self.cpd.sample(vol))


class Plate:
    def __init__(self, name = None, wells = 384, ldv = True):
        self.name = name
        self.uid = ''.join(random.choices(ascii_uppercase, 
                                        k=8))
        self.ldv = ldv
        self.wells = {i:Well(plateid = self.uid, ldv = self.ldv) for i in hwells}
    @property
    def df(self):
        return pd.DataFrame(\
                [[i, j.name, j.vol] for i in self.wells for j in self.wells[i].contents], 
                columns = ['well','compound','vol'])
    def fill(self, loc, cpd, vol = None):
        # better in Dest?
        if vol is None:
            if self.ldv:
                vol = 12
            else:
                vol = 60
        self.wells[loc].fill(cpd.sample(vol))

class Src(Plate):
    def __init__(self, **args):
        super().__init__(**args)
    def assign(self, wells):
        if isinstance(wells, list):
            for i in wells:
                self.wells[i.loc] = i
        if isinstance(wells, Well):
            self.wells[wells.loc] = wells

class Dest(Plate):
    def __init__(self):
        super().__init__()
        self.wells = {i:Well() for i in hwells}
        self.blocks = None

class Block:
    def __init__(self, a, b, wells):
        self.a = a 
        self.b = b
        self.wells = wells
        self.k = 3
        self.vol = 1.5 # µl
        # assign wells - Dest method?

class OverDrawnException(Exception):
    pass

class OverFillException(Exception):
    pass

class UnderFillWarning(Warning):
    pass

hwells = [f'{i}{j}' for i in ascii_uppercase[:16] for j in range(1,25)]
