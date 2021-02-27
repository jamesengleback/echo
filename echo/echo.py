import random
from string import ascii_uppercase

import pandas as pd
import numpy as np

class Well():
    def __init__(self, Id=None, plate = None):
        self.id = Id
        self.plate = plate
        self.uid = ''.join(random.choices(ascii_uppercase, k=8))
    def fill(self, name, vol):
        pass
    def xfer(self, name, destination, vol):
        pass

class Plate:
    def __init__(self, name = None, wells = 384):
        self.name = name
        self.uid = ''.join(random.choices(ascii_uppercase, k=8))
        self.wells = {i:Well(Id = i, plate = self) for i in hwells}
    @property
    def df(self):
        pass
    @property
    def picklist(self):
        pass
    def make_blocks(self, shape = None):
        pass
    def fill(self, well, name, vol):
        pass
    def xfer(self, name, destination, vol):
        pass

class Src(Plate):
    def __init__(self):
        super().__init__()
        pass

class Dest(Plate):
    def __init__(self):
        super().__init__()
        pass

vwells = []
hwells = []
