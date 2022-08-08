#%% Imports
import os
import pandas as pd
from pandas import DataFrame

#%% Constants
file_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_dir)
print(file_dir)

DATA: DataFrame = pd.read_csv(R"data\generics.csv")


# %%
class Drug:
    def __init__(self) -> None:
        pass

def getGenericName(drug: str):
    global DATA
    drug = drug.upper() # Uppercase to match data
    for ingreds in DATA["ActiveIngredient"].unique(): # Iterate through all active ingredients 
        if type(ingreds) == str:
            ingreds: str
            ingred_list = [ingred.strip() for ingred in ingreds.split(";") if ingred.strip() != ""]
            if len(ingred_list) == 1 and drug in ingred_list[0]: # Only search in ingredient list when there's a single ingredient, searches drug as a substring of the active ingredient
                print("Found active ingredient", ingred_list[0])
                return ingred_list[0]
    for drug_name in DATA["DrugName"].unique(): # Search instead in DrugName if not found in active ingredient
        if type(drug_name) == str and drug in drug_name: # If drug is a substring of the drug name
            entry = DATA.loc[DATA["DrugName"] == drug_name]
            generic_name: str = entry.iat[0,2] # Retrieves value in row 1, col 3 in df of 1 row
            print(F"Brand drug, converted to generic name {generic_name}")
            return generic_name
    print("Drug name not found")
    return ""
                

if __name__ == "__main__":
    # getGenericName("apixaban")
    # getGenericName("seroquel")
    getGenericName("Guanabenz")

