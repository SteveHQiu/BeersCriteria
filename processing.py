#% Imports
import re, json, os
import pandas as pd
from pandas import DataFrame
from math import nan
import drugstd as drugs # Import local version



def process3(csv_path = R"data\screen4.csv",
             col = "Medications",
             delim = ","
             ):
    # Process df with str list of unstandardized medications and split them into individual entries  
    new_df = DataFrame()
    df = pd.read_csv(csv_path)
    root_name = os.path.splitext(csv_path)[0]
    cols = [c for c in df.columns if c != col] # Get all other columns 
    for index, row in df.iterrows():
        if type(row[col]) == str:
            items_str: str = row[col]
            items: list[str] = [item.strip() for item in items_str.split(delim)]
            items = [drugs.standardize([drug])[0] for drug in items]
            for item in items:
                entry_dict = {c: [row[c]] for c in cols}
                entry_dict["ExStandardized"] = item
                entry_df = DataFrame(entry_dict)
                new_df = pd.concat([new_df, entry_df])
    new_df.to_csv(f"{root_name}_std.csv")



def process1(csv_path = R"data\interac.csv",
             cols = ["Drug 1", "Drug 2", "Drug 3"],
             delim = ","
             ):
    # Convert string of drugs contained in specified cols separated by specified delimiter 
    df = pd.read_csv(csv_path)
    root_name = os.path.splitext(csv_path)[0]
    for index, row in df.iterrows():
        for col in cols:
            if type(row[col]) == str:
                items_str: str = row[col]
                items: list[str] = [item.strip() for item in items_str.split(delim)]
                items = [drugs.standardize([drug])[0] for drug in items]
                items_json = json.dumps(items)
                row[col] = items_json
    df.to_csv(f"{root_name}_std.csv")

def process2(csv_path = R"data\screen2.csv", col = "Drug", fda = False):
    # Generate synonyms using drugstandards and FDA (optional)
    root_name = os.path.splitext(csv_path)[0]
    fda_data: DataFrame = pd.read_csv(R"data\generics.csv")
    df: DataFrame = pd.read_csv(csv_path)
    std_output = DataFrame()
    for index, row in df.iterrows():
        drug: str = row[col]
        drug = drug.upper()
        entry_dict = dict() # Will be passed for initializing dataframe entry
        
        entry_dict["ExStandardized"] = [drugs.standardize([drug])[0]] # Take first outcome item
        
        if fda:
            std_set = set()
            for ind, r in fda_data.iterrows():
                if drug in r["DrugName"]:
                    std_set.add(r["DrugName"])
                if drug in r["ActiveIngredient"]:
                    std_set.add(r["ActiveIngredient"])
            std_json = json.dumps(list(std_set))
            entry_dict["Standardized"] = [std_json]
        
        new_entry = DataFrame(entry_dict)
        new_entry.index = pd.RangeIndex(start=index, stop=index+1, step=1)
        std_output = pd.concat([std_output, new_entry]) 
    merged = pd.concat([df, std_output], axis=1)
    merged.to_csv(f"{root_name}_std.csv", index=False)

process2(r"data\screen3.csv")
            

if 0: # Processing raw products to get only unique drugname and active ingredients 
    DF: DataFrame = pd.read_excel(R"data\products.xlsx")
    DF = DF.dropna(subset=["DrugName", "ActiveIngredient"]) # Drop rows where these are empty
    DF = DF.drop_duplicates(subset=["DrugName", "ActiveIngredient"]) # Drop duplicates based on drug name

    DATA = DF[["DrugName", "ActiveIngredient"]] # Output subset as data 
    DATA = DATA.reset_index(drop=True) # Reindex to become iterable
    # DATA.to_excel(R"data\generics.xlsx")
    DATA.to_csv(R"data\generics.csv")