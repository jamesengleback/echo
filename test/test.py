from unittest import TestCase
import echo

class testCpd(TestCase):
    def test(self):
        vol = 40
        fa=echo.Cpd(name='fa',vol=vol)
        fa.__repr__()
        fa.__str__()
        fa_ = fa(20)
        fa__ = fa_(2)
        assert sum((fa.vol, fa_.vol, fa__.vol)) == vol
        assert len(fa.children) > len(fa_.children) > len(fa__.children)
        fa_0 = fa - 2
        m1 = fa_0 + fa_
        assert isinstance(fa_0, echo.Cpd)
        assert fa_0.vol == 2
        assert isinstance(m1, echo.Mixture)
        # todo
        # test oversampling error

class testMixture(TestCase):
    def test(self):
        fa=echo.Cpd(name='fa',vol=10)
        x=echo.Cpd(name='x',vol=10)
        dmso=echo.Cpd(name='dmso',vol=50)
        mix = echo.Mixture(fa,dmso)
        vol = mix.vol
        spl = mix(4)
        mix.add(x(2))
        mix.__repr__()
        mix.vol
        mix.add(x)
        echo.Mixture()
        echo.Mixture([])
        mix2 = echo.Mixture(fa(2),dmso(2))
        mix3 = echo.Mixture(mix, mix2)

class testWell(TestCase):
    def test(self):
        dmso=echo.Cpd(name='dmso',vol=50)
        fa=echo.Cpd(name='fa',vol=10)
        well = echo.Well(loc='A1')

class testSrcWell(TestCase):
    def test(self):
        pass

class testDestWell(TestCase):
    def test(self):
        pass

class testPlate(TestCase):
    def test(self):
        src = echo.SrcPlate()
        for i,j,k in zip(echo.vwells, 
                         [f'cpd{i}' for i in range(12)],
                        src):
            cpd = echo.Cpd(name=k, vol=100)
            k.fill(cpd.sample(30))
        dest = echo.DestPlate()
        for i,j in zip(src[:3],dest):
            i.xfer(j,1.5)
        xfer_record = src.xfer_record
        xfer_record = dest.xfer_record
        src.wells
        dest.wells
        x = dest[0]
        print(len(x.contents.cpds))
        print(x)
        #print(dest[:2])

class testSrcPlate(TestCase):
    def test(self):
        pass

class testDestPlate(TestCase):
    def test(self):
        pass

class testEdgeCases(TestCase):
    def test(self):
        src = echo.SrcPlate()
        for i,j,k in zip(echo.vwells, 
                         ['cpd1','cpd2','cpd3'],
                        src):
            cpd = echo.Cpd(name=k, vol=100)
            k.fill(cpd.sample(1.5))
        dest = echo.DestPlate()
        for i,j in zip(dest, src):
            i.__repr__()
            #j.__repr__()
            break

