# echo - tools for making echo pick list csvs

For designing custom picklists (`csv`) for a *Labcyte Echo* acoustic liquid handler - to be imported into *Labcyte Echo Plate Reformat* as a region definitions in custom mode.

Designing weird picklists can be tricky so `echo` aims to make it a bit easier. 

## picklists
The *Echo* accepts a `csv` as a picklist for fluid transfer with the format:

| Source Well | Dest Well | Transfer Volume |
|-------------|-----------|-----------------|
|   A1        |    B4     |   2.5           |
|   A2        |    C4     |   1500          |
|   A2        |    B5     |   40.5          |

Where the transfer volume is in nl and must be a multiple of 2.5. Additional columns can include `Source Plate Name` and `Destination Plate Name` for using multiple plates.

Different source plate types are available and have different minimum and maximum volumes, outside of which the *Echo* will return an error and not dispense from that well.

| Source Plate Type | N Wells | Min vol | Max vol |
|-------------------|---------|---------|---------|
|  ldv 384          |   384   |   2.5   |  12.5   |
|   384 pp          |   384   |   15?   |  65?    |
|    DMSO tray      |   6     |   ?     |   ?     |

This causes some constraints and can mean that one compound might need to be aliquot into multiple wells to serve the destination plate, which I found tricky to script.

`echo` keeps track of plate objects and the contents of their wells to generate picklists. It relies on the user specifying which compounds and how much are in the source plate (`echo.Src`) wells. Individual wells in the plate can be addressed to transfer a specified volume to a destination well, but an a compound and all wells containing it can also be addressed, where after one well runs down to the minimum volume, the next well is then used and so on. Handy.

------------------

## how to

> todo


---------------

```python
import echo

src = echo.Src()

for i, j in zip(echo.vwells, ['cpd1','cpd2','cpd3']):
	src.fill(well = i, name = j, vol = 20)

dest = echo.Dest()

dest.make_blocks(shape = (8,2))

for i in dest.blocks:
	for j, k in zip(i[:,0], i[0,:]):
		src.xfer('cpd1', j, 10)
		src.xfer('cpd1', k, 10)

dest.picklist.to_csv('picklist.csv')
print(dest.df)
```
