from numpy import genfromtxt
import pandas as pd

file = "/home/mila/d/daria.yasafova/mini_ada/data/multimap.csv"
my_data = genfromtxt(file, delimiter="\t")
print(my_data)
df = pd.read_csv(file, sep="\t", header=None)
print(df)
coltp = []
for col in df:
    print(df[col])
    print("hi")
    # breakpoint()
    rowtp = ""
    for row in df[col]:
        #        if row != "NaN":
        if not isinstance(row, float):
            # breakpoint()
            rowtp = rowtp + "," + row
        else:
            break
    print("row:", rowtp)
    coltp.append(rowtp)
    continue
# breakpoint()
