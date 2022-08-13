import os
import pandas as pd


cwd = os.path.abspath('') 
files = os.listdir(cwd) 
print(files)
file_name = input("File name (without extension)")

df = pd.DataFrame()
for file in files:
    if file.endswith(".xls"):
        df = df.append(pd.read_excel(file), ignore_index=True)
    if file.endswith(".csv"):
        df = df.append(pd.read_csv(file), ignore_index=True)


df.to_csv(file_name+".csv")
