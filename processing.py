#% Imports
import re, json, os
import pandas as pd
from pandas import DataFrame
from math import nan
import drugstd as drugs # Import local version


def addDictEntry(d: dict, entry: dict):
    entry = {k: entry[k] for k in entry if k not in d} # Get non-overlapping entries
    d.update(entry)
json_path = "data/drugdict.json"
with open(json_path, "r") as file:
    drug_dict = json.load(file)
cont1 = []
cont2 = []
cont3 = []
cont4 = []
cont5 = []
for key in drug_dict.copy():
    key: str
    spaces = re.findall(R" ", key)
    dashes = re.findall(R"\-", key) # 
    brkets = re.findall(R" \([^\[\]\(\)]*\)", key)
    sqr_brkets = re.findall(R" \[[^\[\]\(\)]*\]", key) # Match parenthes preceded by a space and without any brackets within it
    if len(dashes) < 3 and (len(brkets) == 1 or len(sqr_brkets) == 1) and \
        (bool(len(brkets)) != bool(len(sqr_brkets))): 
        # Screen out orgchem compounds (usually has 3+ dashes and 2+ brackets)
        # Last and statement is an XOR comparison since both should be positive to get to this point
        val = drug_dict[key]
        del drug_dict[key] # Delete entry
        for match in brkets + sqr_brkets:
            key = key.replace(match, "") # Replace original variable 
        addDictEntry(drug_dict, {key: val}) # Only adds to dict if no conflict, modifies in-inplace
        cont1.append(key)
    
    
        
    if len(key) <= 2: # Remove entries less than 2 
        del drug_dict[key]
        cont3.append(key)
        
    matches2 = re.findall(R"SODIUM", key)
    matches5 = re.findall(R" ACETATE", key)
    if len(matches2):
        cont2.append(key)
    if len(matches5):
        cont5.append(key)
        
# print(set(cont5).symmetric_difference(cont3))
print(cont2)
print(len(cont2))
print(cont3)
print(len(cont3))
print(drug_dict)


if 0:
    with open(json_path, "w+") as file:
        pass

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

            

if 0: # Processing raw products to get only unique drugname and active ingredients 
    DF: DataFrame = pd.read_excel(R"data\products.xlsx")
    DF = DF.dropna(subset=["DrugName", "ActiveIngredient"]) # Drop rows where these are empty
    DF = DF.drop_duplicates(subset=["DrugName", "ActiveIngredient"]) # Drop duplicates based on drug name

    DATA = DF[["DrugName", "ActiveIngredient"]] # Output subset as data 
    DATA = DATA.reset_index(drop=True) # Reindex to become iterable
    # DATA.to_excel(R"data\generics.xlsx")
    DATA.to_csv(R"data\generics.csv")