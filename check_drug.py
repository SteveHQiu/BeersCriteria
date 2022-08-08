import json
import pandas as pd
from pandas import DataFrame
from itertools import combinations, permutations

import drugstandards as drugs

DF_S = pd.read_csv(R"data\screen_std.csv")
DF_I = pd.read_csv(R"data\interac_std.csv")

def checkDrug(drug: str):
    global DF_S
    std_drug = drugs.standardize([drug])[0] # Should only return one item
    print(std_drug)
    
    if std_drug in list(DF_S["ExStandardized"]):
        entry = DF_S.loc[DF_S["ExStandardized"] == std_drug] # Take first item
        entry = entry.reset_index(drop=True) # Reset index to access by labels rather than relative positions
        print(f"Found {len(entry)} entries")
        if len(entry) > 1:
            print(entry.nunique())
        drug_origin = entry.at[0, "Drug"]
        rec = entry.at[0, "Recommendation"]
        rationale = entry.at[0, "Rationale"]
        report = f"Beers entry: {drug_origin}\nRecommendation: {rec}\nRationale: {rationale}"
        print(report)
        return report
    return "No entries found"

def checkInterac(drugs: list[str]):
    global DF_I
    if len(drugs) > 1:
        for index, row in DF_I.iterrows():
            cols = ["Drug 1", "Drug 2", "Drug 3"]
            cols = [col for col in cols if type(row[col]) == str] # Default cell value is float of nan, only parse strings 
            for drug_perm in permutations(drugs, len(drugs)):
                col_dict = {col: 0 for col in cols} # Re-instantiate empty dict each permutation
                tracker: list[str] = [] # Tracker so that once drug is entered into a class, it is consumed
                for drug_cat in cols:
                    members_str: str = row[drug_cat]
                    members: list[str] = json.loads(members_str)
                    for drug in drug_perm:
                        if col_dict[drug_cat] != 1: # Only continue to find members if this category has not been filled
                            drug = drug.upper()
                            if drug in members and drug not in tracker: # If there is membership, it hasn't been tracked already, and the category has not already been satisfied
                                tracker.append(drug) 
                                col_dict[drug_cat] = 1
                values = [col_dict[key] for key in col_dict]
                if all(values): # If all values are non-zero (i.e., all categories have been satisfied)
                    print("Rule satisfied Lmao")
                    # Add this rule to the report since multiple may be satisfied 
                    return
                    
        # Can probably solve this more efficiently with Hall's theorem via graphs
    print("No interactions")
    return 

if __name__ == "__main__":
    checkInterac(["Losartan", "Trandolapril"]) # Yes
    checkInterac(["Trandolapril", "Losartan"]) # Yes
    checkInterac(["Losartan", "Losartan"]) # No
    checkInterac(["Triamterene", "Losartan"]) # Yes
    checkInterac(["Losartan", "Quazepam", "Quazepam"]) # No
    checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Trospium"]) # No
    checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Prochlorperazine"]) # Yes
    checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin"]) # No
    checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin", "Lacosamide"]) # Yes