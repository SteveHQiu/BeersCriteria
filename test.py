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

def getGenericName(drug: str):
    global DATA
    drug = drug.upper() # Uppercase to match data
    if drug in DATA["ActiveIngredient"].unique(): # Check if drug name already generic first
        print("Generic drug")        
        return drug
    elif drug in DATA["DrugName"].unique(): # If drug name in column; without unique() method, will check if value is in the index instead of values
        # Get active ingredient of that row and return it 
        entry = DATA.loc[DATA["DrugName"] == drug]
        generic_name = entry.iat[0,2] # Retrieves value in row 1, col 3 in df of 1 row
        print(F"Brand drug, converted to generic name {generic_name}")
        return generic_name
    else:
        print("Drug name not found")
        return False

getGenericName("apixaban")
getGenericName("seroquel")
getGenericName("Carbinoxamine")


# %%
