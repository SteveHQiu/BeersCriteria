#% Imports
import re, json, os
import pandas as pd
from pandas import DataFrame
from math import nan
import drugstd as drugs # Import local version

def process5(json_path = "data/drugdict.json", save = False, add = False):
    # Processes drug translation dictionary for brackets, short entries, invalid characters, counterions
    
    def _addDictEntry(d: dict, entry: dict):
        entry = {k: entry[k] for k in entry if k not in d} # Get non-overlapping entries
        d.update(entry)

    with open(json_path, "r") as file:
        drug_dict = json.load(file)
    
    for key in drug_dict.copy():
        slashes = re.findall(R"/", key)
        if slashes:
            print(key)

def process4(json_path = "data/drugdict.json", save = False, add = False):
    # Processes drug translation dictionary for brackets, short entries, invalid characters, counterions
    
    def _addDictEntry(d: dict, entry: dict):
        entry = {k: entry[k] for k in entry if k not in d} # Get non-overlapping entries
        d.update(entry)

    with open(json_path, "r") as file:
        drug_dict = json.load(file)
        
    # drug_dict = {"ACETOACETATE": 1, "SOMETHING1 ACETATE": 2, "ACETATE SOMETHING2": 3, "ACETATES": 4, "SOMETHING1": 99} # For testing

    cont_short = []
    cont_invalid = []
    cont_brackets = []
    cont_ions = []

    invalid_chars = [",", ";", "{", "}", "'", '"', "/"]

    counterions = ["ALUMINUM", "ARGININE", "BENZATHINE", "CALCIUM", "CHLOROPROCAINE", "CHOLINE",
                "DIETHANOLAMINE", "ETHANOLAMINE", "ETHYLENEDIAMINE", "LYSINE", "MAGNESIUM",
                "HISTIDINE", "LITHIUM", "MEGLUMINE", "POTASSIUM", "PROCAINE", "SODIUM", 
                "TRIETHYLAMINE", "ZINC", "ACETATE", "ASPARTATE", "BENZENESULFONATE", "BENZOATE",
                "BESYLATE", "BICARBONATE", "BITARTRATE", "BROMIDE", "CAMSYLATE", "CARBONATE",
                "CHLORIDE", "CITRATE", "DECANOATE", "EDETATE", "ESYLATE", "FUMARATE", "GLUCEPTATE",
                "GLUCONATE", "GLUTAMATE", "GLYCOLATE", "HEXANOATE", "HYDROXYNAPHTHOATE", "IODIDE",
                "ISETHIONATE", "LACTATE	LACTOBIONATE", "MALATE", "MALEATE", "MANDELATE", "MESYLATE",
                "METHYLSULFATE", "MUCATE", "NAPSYLATE", "NITRATE", "OCTANOATE", "OLEATE", "PAMOATE",
                "PANTOTHENATE", "PHOSPHATE", "POLYGALACTURONATE", "PROPIONATE", "SALICYLATE", 
                "STEARATE", "ACETATE", "SUCCINATE", "SULFATE", "TARTRATE", "TEOCLATE", "TOSYLATE",
                "SALT"] 
    # From https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6100526/

    for key in drug_dict.copy():
        key: str
        original = key
        val = drug_dict[key]
        spaces = re.findall(R" ", key)
        slashes = re.findall(R"/", key)
        dashes = re.findall(R"\-", key) # 
        brkets = re.findall(R" \([^\[\]\(\)]*\)", key)
        sqr_brkets = re.findall(R" \[[^\[\]\(\)]*\]", key) # Match parenthes preceded by a space and without any brackets within it
        
        
        if len(key) <= 2: # Remove entries less than 2 
            del drug_dict[key]
            cont_short.append(key)
            continue # Have to continue to next loop, otherwise missing key will throw error for subsequent loops
            
        contains_invalid = False
        for char in invalid_chars:
            if char in key: # Delete entries with invalid characters 
                contains_invalid = True
            if contains_invalid:
                break
        if contains_invalid:
            del drug_dict[key]
            cont_invalid.append(key)
            continue
        
        
        if len(dashes) < 3 and (len(brkets) == 1 or len(sqr_brkets) == 1) and \
            (bool(len(brkets)) != bool(len(sqr_brkets))): 
            # Screen out orgchem compounds (usually has 3+ dashes and 2+ brackets)
            # Last and statement is an XOR comparison since both should be positive to get to this point
            del drug_dict[key] # Delete entry
            for match in brkets + sqr_brkets:
                key = key.replace(match, "") # Replace original variable 
            _addDictEntry(drug_dict, {key: val}) # Only adds to dict if no conflict, modifies in-inplace
            cont_brackets.append((original, key))
            continue
            
        
        all_matches = [] # Collect all matches to process at the very end, otherwise removal of key during processing of one counterion may prevent processing of subsequent ions
        for counterion in counterions:
            matches = re.findall(RF"(?:\s|^){counterion}(?:\s|$)", key) 
            # Find counterion at beginning or end, need normal brackets since braces will result in literal interpretation
            # Shouldn't search exclusively at beginning or end since want this to capture all counterions, count used to mod entries with only one counterion
            all_matches += matches # Concatenate matches
        if len(all_matches) == 1: # Multiple matches usually because compound is made of one or more counterions
            # Don't need to delete original entry since it may be useful, this pipeline only adds extra lookups 
            for match in all_matches:
                new_key = key.replace(match, "")
                if new_key.strip(): # If the new proposed key is not empty, carry out with actual replacement
                    key = key.replace(match, "") # Replace original variable 
            _addDictEntry(drug_dict, {key: val}) # Only adds to dict if no conflict, modifies in-inplace
            cont_ions.append((original, key))
            continue

    print(F"Bracket entries modified: {len(cont_brackets)}")
    print(F"Short entries removed: {len(cont_short)}")
    print(F"Invalid entries removed: {len(cont_invalid)}")
    print(F"Entries with counterions modified: {len(cont_ions)}")
    # print(cont_ions)
    
    drug_dict = {d: drug_dict[d] for d in drug_dict if d.strip()} # Screen out whitespace entries

    if add: # Add custom entries as needed (will not override definitions if they exist)
        _addDictEntry(drug_dict, {"BELLADONNA ALKALOIDS": "BELLADONNA ALKALOIDS", "BELLADONNA": "BELLADONNA ALKALOIDS", "LIXIANA": "EDOXABAN", "EDOXABAN": "EDOXABAN"})
        _addDictEntry(drug_dict, {"BUTROPIUM": "BUTROPIUM", })
        _addDictEntry(drug_dict, {"CLIDINIUM": "CLIDINIUM", "LIBRAX": "CLIDINIUM", })
        _addDictEntry(drug_dict, {"GUANABENZ": "GUANABENZ", "WYTENSIN": "GUANABENZ", })
        _addDictEntry(drug_dict, {"BUTISOL": "BUTABARBITAL", "BUTABARBITAL": "BUTABARBITAL", })
        _addDictEntry(drug_dict, {"DUVADILAN": "ISOXSUPRINE", "VASODILAN": "ISOXSUPRINE", "ISOXSUPRINE": "ISOXSUPRINE", })
        _addDictEntry(drug_dict, {"DESICCATED THYROID": "DESICCATED THYROID", "THYROID EXTRACT": "DESICCATED THYROID"})
        _addDictEntry(drug_dict, {"MINERAL OIL": "MINERAL OIL"})
        _addDictEntry(drug_dict, {"NUPLAZID": "PIMAVANSERIN", "PIMAVANSERIN": "PIMAVANSERIN"})
        _addDictEntry(drug_dict, {"FENTONIUM": "FENTONIUM"})
        _addDictEntry(drug_dict, {"EQUIPIN": "HOMATROPINE", "HOMATROPINE": "HOMATROPINE",})
        _addDictEntry(drug_dict, {"NORETHINDRONE": "NORETHISTERONE", "NORETHISTERONE": "NORETHISTERONE",})
        _addDictEntry(drug_dict, {"DROSPIRENONE": "DROSPIRENONE", "SLYND": "DROSPIRENONE",})
        _addDictEntry(drug_dict, {"BUTALBITAL": "BUTALBITAL", "ESGIC": "BUTALBITAL", "FIORICET": "BUTALBITAL"})
        _addDictEntry(drug_dict, {"PIPERAZINE ESTRONE": "ESTROPIPATE", "ESTROPIPATE": "ESTROPIPATE", "HARMOGEN": "ESTROPIPATE"})
        _addDictEntry(drug_dict, {"FETZIMA": "LEVOMILNACIPRAN", "LEVOMILNACIPRAN": "LEVOMILNACIPRAN"})
        _addDictEntry(drug_dict, {"OPIUM": "OPIUM"})
        _addDictEntry(drug_dict, {"SKELAXIN": "METAXALONE", "METAXALONE": "METAXALONE"})

    if save:
        with open(json_path, "w+") as file:
            json.dump(drug_dict, file)

process4(save=True, add=True)

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
            for item in items:
                item_std = drugs.standardize([item])[0]
                entry_dict = {c: [row[c]] for c in cols}
                entry_dict["Drug"] = item
                entry_dict["ExStandardized"] = item_std
                entry_df = DataFrame(entry_dict)
                new_df = pd.concat([new_df, entry_df])
    new_df.to_csv(f"{root_name}_std.csv")

# process3()

def process2(csv_path = R"data\interac.csv",
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


def process1(csv_path = R"data\screen.csv", col = "Drug", fda = False):
    # Generate synonyms using drugstandards and FDA (optional)
    root_name = os.path.splitext(csv_path)[0]
    fda_data: DataFrame = pd.read_csv(R"data\generics.csv")
    df: DataFrame = pd.read_csv(csv_path)
    std_output = DataFrame()
    for index, row in df.iterrows():
        drug: str = row[col]
        if type(drug) != str:
            continue # Skip this column if not a string
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

# process1()

if 0: # Processing raw products to get only unique drugname and active ingredients 
    DF: DataFrame = pd.read_excel(R"data\products.xlsx")
    DF = DF.dropna(subset=["DrugName", "ActiveIngredient"]) # Drop rows where these are empty
    DF = DF.drop_duplicates(subset=["DrugName", "ActiveIngredient"]) # Drop duplicates based on drug name

    DATA = DF[["DrugName", "ActiveIngredient"]] # Output subset as data 
    DATA = DATA.reset_index(drop=True) # Reindex to become iterable
    # DATA.to_excel(R"data\generics.xlsx")
    DATA.to_csv(R"data\generics.csv")