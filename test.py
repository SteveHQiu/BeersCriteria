import pandas as pd
import json
from pandas import DataFrame
import timeit

from check_drug import checkInterac
items = ["CHLORDIAZEPOXIDE", "HEROIN", "CODEINE", "OXYCODONE", "HYDROCODONE", "TRAMADOL", "MORPHINE", "HYDROMORPHONE", "FENTANYL", "DOXAZOSIN", "BENAZEPRIL", "CAPTOPRIL", "ENALAPRIL"]
print(len(items))
start = timeit.default_timer()
checkInterac(items)
stop = timeit.default_timer()

print('Time: ', stop - start) 


if 0:
    start = timeit.default_timer()

    # DATA: DataFrame = pd.read_excel(R"data\generics.xlsx")
    DATA: DataFrame = pd.read_csv(R"data\generics.csv")


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

    stop = timeit.default_timer()

    print('Time: ', stop - start)  