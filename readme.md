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


## Examples

```python
import echo

src = echo.SrcPlate(name='src1',ldv=True)
dest = echo.DestPlate(name='dest1')

for i,j,k in zip(echo.vwells, 
                 ['cpd1','cpd2','cpd3'],
                 src):
    cpd = echo.Cpd(name=j, vol=100)
    k.fill(cpd.sample(5))

for i,j in zip(src[:3],dest):
    i.xfer(j,1.5)

xfer_record = pd.DataFrame(src.xfer_record)
xfer_record
```

|    | SrcPlate   | Cpd      | SrcWell   | Destination Plate Name   | DestWell   |   Transfer Volume /nl |\n|---:|:-----------|:---------|:----------|:-------------------------|:-----------|----------------------:|\n|  0 | src1       | ['cpd1'] | A1        | dest1                    | A1         |                  1500 |\n|  1 | src1       | ['cpd2'] | A2        | dest1                    | A2         |                  1500 |\n|  2 | src1       | ['cpd3'] | A3        | dest1                    | A3         |                  1500 |
