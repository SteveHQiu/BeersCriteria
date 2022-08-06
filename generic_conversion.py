#%% Imports
import pandas as pd
from pandas import DataFrame

#%% Constants
DF: DataFrame = pd.read_excel(R"data\products.xlsx")
DF = DF.dropna(subset=["DrugName", "ActiveIngredient"]) # Drop rows where these are empty
DF = DF.drop_duplicates(subset="DrugName") # Drop duplicates based on drug name

DATA = DF[["DrugName", "ActiveIngredient"]] # Output subset as data 
DATA = DATA.reset_index() # Reindex to become iterable


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
    getGenericName("DMax")

