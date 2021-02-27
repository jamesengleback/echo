# echo - tools for making echo pick list csvs

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
