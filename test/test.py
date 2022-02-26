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

class testWell(TestCase):
    def test(self):
        dmso=echo.Cpd(name='dmso',vol=50)
        fa=echo.Cpd(name='fa',vol=10)

class testSrcWell(TestCase):
    def test(self):
        pass

class testDestWell(TestCase):
    def test(self):
        pass

class testPlate(TestCase):
    def test(self):
        pass

class testSrcPlate(TestCase):
    def test(self):
        pass

class testDestPlate(TestCase):
    def test(self):
        pass

def main():
    dmso = echo.Cpd(name = 'dmso', vol = 50)
    fa = echo.Cpd(name = 'fa', vol=10)

    dest = echo.Dest()
    dest.fill('A1', dmso, 2)
    dest.fill('A1', fa, 5)
    print([i.contents for i in dest.wells.values()])
    print(dest.df)


if __name__ == '__main__':
    main()
