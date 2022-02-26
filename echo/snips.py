import os.path as osp
import ast
import copy
import random
from string import ascii_uppercase
import json
import numpy as np
import pandas as pd

round2p5 = lambda x : round(x/2.5) * 2.5

class Cpd:
    '''
    class containing compound, (liquid)
        methods:
            sample(vol): return Cpd(vol=vol), updatesmparent volume
    '''
    def __init__(self, 
                 name=None,
                 vol=0,
                 parent=None,
                 plate=None,
                 well=None):

        self.name = name 
        self.vol = vol
        self.children = []
        self.parent = parent
        self.plate = plate
        self.well = well

    def __repr__(self):
        if self.plate is not None:
            plate_name = self.plate.name
        else: 
            plate_name = None
        if self.well is not None:
            well_loc = self.well.loc
        else:
            well_loc = None
        return f'{self.name} {self.vol}µl  plate: {plate_name} well: {well_loc}'

    def sample(self, vol):
        if vol < self.vol:
            self.vol -= vol 
            sample = Cpd(self.name, vol, parent = self)
            self.children.append(sample)
            return sample
        else:
            raise OverDrawnException(f'Requested vol: {vol} Available vol: {self.vol}µl')

    def xfer(self, dest_well, vol):
        # find all children, make transfers
        children = self.get_children()
        available_vol = sum([i.well.available_vol for i in children])
        if vol <= available_vol:
            unique_plates = set([i.plate for i in children])
            vol_todo = vol # copy????
            for i in unique_plates:
                wells = [j for j in children if j.plate == i]
                for j in wells:
                    if isinstance(j.well, SrcWell):
                        available_vol = j.well.available_vol 
                        if vol_todo > available_vol:
                            xfer_vol = available_vol 
                        else:
                            xfer_vol = vol_todo
                        if xfer_vol != 0: 
                            j.well.xfer(dest_well, xfer_vol)
                            vol_todo -= xfer_vol
                        if vol_todo == 0:
                            break
        else:
            raise NotEnoughException(f'cpd:{self}, available_vol: {available_vol}µl, requested: {vol}µl')
        if vol_todo != 0:
            raise UnderFillWarning(f'cpd:{self}, available_vol: {available_vol}µl, requested: {vol}µl')
    def get_children(self):
        l = []
        if len(self.children) > 0:
            for i in self.children:
                l.append(i)
                l.append(i.get_children())
        # from https://stackoverflow.com/questions/12472338/flattening-a-list-recursively
        flatten=lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l] 
        return flatten(l)

class Mixture:
    '''
    '''
    def __init__(self, 
                 cpds=[]):
        self.cpds = cpds

    def __repr__(self):
        if len(self.cpds) != 0:
            d = {i.name:i.vol for i in self.cpds}
        else:
            d = {}
        return f'{d}'
    @property
    def vol(self):
        return sum([i.vol for i in self.cpds])
    def sample(self, vol):
        if vol < self.vol:
            fracs = [i.vol / self.vol  for i in self.cpds]
            sample = Mixture([i.sample(j * vol) for i, j in zip(self.cpds, fracs)]) # **prob
            self.consolidate()
            sample.consolidate()
            return sample
        else:
            raise OverDrawnException(f'Requested vol: {vol}µl Available vol: {self.vol}µl')
    def append(self, cpd):
        if isinstance(cpd, Cpd):
            self.cpds.append(cpd)
        elif isinstance(cpd, Mixture):
            self.cpds += cpd.cpds 
        else:
            # error 
            print('uh oh')
        self.consolidate()
    def consolidate(self):
        # pool compounds with matching names
        l = []
        uniq_names = set([i.name for i in self.cpds])
        for i in uniq_names:
            l2 = []
            for j in self.cpds:
                if j.name == i:
                    l2.append(j)
            assert len(l2) != 0
            l.append(Cpd(name=i, vol=sum([k.vol for k in l2])))
        self.cpds = l

class Well:
    '''
    '''
    def __init__(self, 
                 loc, 
                 plate=None, 
                 contents=None):
        self.loc = loc
        self.plate = plate
        self.contents = Mixture([]) ### why does the default not register???
        # leaving this lime Mixture() was really problematic
        # it made all instances of mixture the same
        # copying issue????
    @property
    def vol(self):
        return self.contents.vol
    def __repr__(self):
        return f'plate: {self.plate} loc: {self.loc}  contents: {self.contents}'
    def fill(self, sample):
        sample.well = self
        sample.plate = self.plate
        self.contents.append(sample)

class SrcWell(Well):
    '''
    '''
    def __init__(self, 
                 ldv=True, 
                 **args):
        super().__init__(**args)
        self.ldv = ldv
        if self.ldv:
            self.minvol = 2.5
            self.maxvol = 12
        else:
            self.minvol = 15
            self.maxvol = 65
        self.xfer_record = []
    def __repr__(self):
        return f'plate: {self.plate} loc: {self.loc}  contents: {self.contents} available_vol: {self.available_vol}µl'
    @property
    def available_vol(self):
        available = self.vol - self.minvol
        if available > 0:
            return available
        else:
            return 0
    def xfer(self, dest_well, vol):
        get_cpd_names = lambda mixture : [i.name for i in mixture.cpds]
        if vol <= self.available_vol:
            dest_well.fill(self.contents.sample(vol))
            self.xfer_record.append({'SrcPlate':self.plate.name, 'Cpd':get_cpd_names(self.contents), 'SrcWell':self.loc, 'Destination Plate Name':dest_well.plate.name, 'DestWell':dest_well.loc,  'Transfer Volume /nl':round2p5(vol * 1000)}) # nl
        else:
            raise OverDrawnException(f'Requested vol: {vol}µl Available vol: {self.available_vol}µl')

class Plate:
    '''
    '''
    def __init__(self, 
                 name=None, 
                 nwells=384):
        super().__init__()
        self.name = name
        self.wells = self.make_wells(nwells)

    def __repr__(self):
        return f'{self.name} {len(self)}'
    def __len__(self):
        return len(self.wells)
    def __getitem__(self, item):
        if isinstance(item, int):
            k = list(self.wells.keys())[item]
            return self.wells[k]
        if isinstance(item, slice):
            k = list(self.wells.keys())[item]
            return [self.wells[i] for i in k]
        else:
            return self.wells[item]
    def __iter__(self):
        for i in self.wells:
            yield self.wells[i]
    def loc(self, idx):
        # return sliceable slice of cols / rows
        pass
    def make_wells(self, nwells, well_type = Well, **args):
        assert nwells in [96, 384, 1536]
        # ncols = 1.5 *nrows
        # nwells = 1.5 * nrows**2
        nrows = int(np.sqrt(nwells/1.5))
        ncols = int(nrows * 1.5)
        rows = list(ascii_uppercase[:nrows])
        cols = range(1, ncols+1)
        well_ids = [f'{i}{j}' for i in rows for j in cols]
        return {i:well_type(loc=i, plate = self, **args) for i in well_ids}
    @property
    def map(self):
        return pd.DataFrame([{'plate':self.name,'well':i.loc,'contents':i.contents,'vol':i.vol} for i in self])

class SrcPlate(Plate):
    '''
    '''
    def __init__(self, 
                 ldv=True, 
                 **args):
        self.ldv = ldv
        super().__init__(**args)
        self.wells = self.make_wells(len(self), well_type = SrcWell, ldv=self.ldv)
    @property
    def xfer_record(self):
        return pd.DataFrame([j for i in self for j in i.xfer_record]) ## flattens list

class DestPlate(Plate):
    '''
    '''
    def __init__(self, 
                 **args):
        super().__init__(**args)


class ExceptionsReport(Plate):
    '''
    aim:
    map compound concs to wells
    account for exceptions
    handle plate map or picklist input
    '''
    def __init__(self, 
                 exceptions_report=None, 
                 picklist=None, 
                 platemap=None, 
                 **args):
        super().__init__(**args)
        self.platemap = platemap # plate(s) or picklist
        self.exceptions_report = exceptions_report # exceptions report csv
        self.picklist = picklist
        self.process()

    def __repr__(self):
        return f''
    def process(self):
        platemap_allocations = {}
        if self.platemap is not None:
            platemap = pd.read_csv(self.platemap, index_col=0)
            for i,j in zip(platemap['well'],platemap['contents']):
                platemap_allocations[i] = ast.literal_eval(j)

        picklist_allocations = {} # dest
        picklist_src_allocations = {}
        if self.picklist is not None:
            if isinstance(self.picklist, str):
                picklist = pd.read_csv(self.picklist, index_col=0)
            elif isinstance(self.picklist,list):
                picklist = pd.concat([pd.read_csv(i, index_col=0) for i in self.picklist])

            for plate in picklist['Destination Plate Name'].unique():
                this_plate_allocation = {}
                chunk = picklist.loc[picklist['Destination Plate Name'] == plate,:]
                for well in chunk['DestWell'].unique():
                    chunkchunk = chunk.loc[chunk['DestWell'] == well,:] # cpds are like: ["['S4204']", "['dmso']"]
                    cpds = [j for i in chunkchunk['Cpd'] for j in ast.literal_eval(i)] # flatten
                    vols = chunkchunk['Transfer Volume /nl']
                    this_plate_allocation[well] = {i:j for i,j in zip(cpds,vols)}
                picklist_allocations[plate] = this_plate_allocation 
            for plate in picklist['Source Plate Name'].unique():
                this_plate_allocation = {}
                chunk = picklist.loc[picklist['Source Plate Name'] == plate,:]
                for well in chunk['DestWell'].unique():
                    chunkchunk = chunk.loc[chunk['SrcWell'] == well,:] # cpds are like: ["['S4204']", "['dmso']"]
                    cpds = [j for i in chunkchunk['Cpd'] for j in ast.literal_eval(i)] # flatten
                    vols = chunkchunk['Transfer Volume /nl']
                    this_plate_allocation[well] = {i:j for i,j in zip(cpds,vols)}
                picklist_src_allocations[plate] = this_plate_allocation 
        else:
            picklist = None

        if self.exceptions_report is not None:
            if isinstance(self.exceptions_report, str):
                exceptions_report = pd.read_csv(self.exceptions_report)
            elif isinstance(self.exceptions_report,list):
                exceptions_report = pd.concat([pd.read_csv(i) for i in self.exceptions_report])
            if picklist is not None:
                # i really hope order is preserved...
                exceptions_report_plate_names = sorted(exceptions_report['Destination Plate Name'].unique().tolist()) # ['Destination[2]', 'Destination[3]', 'Destination[4]', 'Destination[5]']
                picklist_plate_names = picklist['Destination Plate Name'].unique().tolist() # ['dest-bsa-blank', 'dest-bsa-test', 'dest-ctrl-blank', 'dest-ctrl-test']
                if len(exceptions_report_plate_names) == len(picklist_plate_names):
                    plate_name_map = dict(zip(exceptions_report_plate_names, picklist_plate_names))
                else:
                    raise IHaventWrittenThisWellException('number of plates in exceptions_report doesnt match picklist. james fix this!')
                exceptions_report['Destination Plate Name'] = [plate_name_map[i] for i in exceptions_report['Destination Plate Name']]
                # todo:
                ## map cpds to src plate
                ## correct cpd vol
                ## write to wells
                
        print(exceptions_report.columns)
            

class NotEnoughException(Exception):
    pass

class OverDrawnException(Exception):
    pass

class UnderFillWarning(Warning):
    pass

class OverFillWarning(Warning):
    pass

class IHaventWrittenThisWellException(Exception):
    pass

hwells = [f'{i}{j}' for i in ascii_uppercase[:16] for j in range(1,25)]
vwells = [f'{i}{j}' for i in range(1,25) for j in ascii_uppercase[:16]]

