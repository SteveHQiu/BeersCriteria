#% Imports
import re, json
import pandas as pd
from pandas import DataFrame
from math import nan

import drugstandards as drugs # Import local version

DF = pd.read_csv(R"data\interac.csv")
for index, row in DF.iterrows():
    cols = ["Drug 1", "Drug 2", "Drug 3"]
    for col in cols:
        if type(row[col]) == str:
            items_str: str = row[col]
            items: list[str] = [item.strip() for item in items_str.split(",")]
            items = [drugs.standardize([drug])[0] for drug in items]
            items_json = json.dumps(items)
            row[col] = items_json
DF.to_csv(R"data\interac_std.csv")
if 0:
    DF: DataFrame = pd.read_csv(R"data\generics.csv")
    SOURCE: DataFrame = pd.read_csv(R"data\table1.csv")
    STD = DataFrame()
    for index, row in SOURCE.iterrows():
        drug: str = row["Drug"]
        drug = drug.upper()
        std1 = drugs.standardize([drug])[0] # Take first outcome item
        std_set = set()
        for ind, r in DF.iterrows():
            if drug in r["DrugName"]:
                std_set.add(r["DrugName"])
            if drug in r["ActiveIngredient"]:
                std_set.add(r["ActiveIngredient"])
        std_json = json.dumps(list(std_set))
        new_entry = DataFrame({"Standardized": [std_json], "ExStandardized": [std1]})
        new_entry.index = pd.RangeIndex(start=index, stop=index+1, step=1)
        STD = pd.concat([STD, new_entry]) 
    merged = pd.concat([SOURCE, STD], axis=1)
    merged.to_csv(R"data\output.csv", index=False)
        
                
            
        

#% Constants
if 0: # Processing raw products to get only unique drugname and active ingredients 
    DF: DataFrame = pd.read_excel(R"data\products.xlsx")
    DF = DF.dropna(subset=["DrugName", "ActiveIngredient"]) # Drop rows where these are empty
    DF = DF.drop_duplicates(subset=["DrugName", "ActiveIngredient"]) # Drop duplicates based on drug name

    DATA = DF[["DrugName", "ActiveIngredient"]] # Output subset as data 
    DATA = DATA.reset_index(drop=True) # Reindex to become iterable
    # DATA.to_excel(R"data\generics.xlsx")
    DATA.to_csv(R"data\generics.csv")