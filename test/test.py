import echo

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
