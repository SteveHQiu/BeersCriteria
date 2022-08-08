import json
import pandas as pd
from pandas import DataFrame
from itertools import combinations

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
        tracker: list[str] = [] # Tracker so that once drug is entered into a class, it is consumed
        for index, row in DF_I.iterrows():
            col_dict = {"Drug 1": 0, "Drug 2": 0 , "Drug 3": 0}
            for drug_cat in col_dict:
                members_str: str = row[drug_cat]
                if type(members_str) != str or not members_str: # Default cell value is float of nan
                    col_dict[drug_cat] = -1
                else:
                    members: list[str] = json.loads(members_str)
                    for drug in drugs:
                        drug = drug.upper()
                        if drug in members and drug not in tracker:
                            tracker.append(drug) 
                            col_dict[drug_cat] += 1
                            pass
                        pass
            new_col_dict = {c: col_dict[c] for c in col_dict if col_dict[c] >= 0}
            values = [new_col_dict[key] for key in new_col_dict]
            if all(values): # If all values are non-zero (i.e., all categories have been satisfied)
                print("Rule satisfied Lmao")
                    
        # Empty should be lower than 0, compare combinations 
    print("No interactions")
    return 

if __name__ == "__main__":
    checkInterac(["Losartan", "Trandolapril"])