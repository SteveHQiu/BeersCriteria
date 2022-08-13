import json, re, operator
from difflib import SequenceMatcher
from typing import Union
# import Levenshtein

    
with open("data/drugdict.json", "r") as file:
    DRUGDICT: dict = json.load(file)

  
def find_closest_string(query: str, dictionary: dict[str, str], thresh=0.85):
    """ This function returns the closest match for 
         a query string against a dictionary of terms
        using levenstein distance
        EDIT - Using built-in sequencematcher instead of levenshtein 
    """
    # dist = {i:Levenshtein.jaro_winkler(query, i) for i in dictionary}
    dist = {i: SequenceMatcher(a=query, b=i).ratio() for i in dictionary}
    dist = sorted(dist.items(), key=operator.itemgetter(1), reverse=True) # Sorted is more efficient than max function
    if dist[0][1] >= thresh:
        return dist[0][0]
    else:
        return None


def standardize(druglist: list[str], thresh=0.85):
    """ This function takes a list of drugs (brand name,
        misspelled drugs, generic names) and converts them
        to the generic names. It is used to provide naming
        consistency to the FAERS reports.
        EDIT - Using built-in sequencematcher instead of levenshtein 
    """
    standardized_druglist: list[Union[str, None]] = []
    druglist = [d.upper() for d in druglist if type(d) == str] # Capitalize, filter for strings
            
    for drug in druglist:        
        drug = re.sub(R" \([^\[\]\(\)]*\)", "", drug) # Ignore parenthesized text
        drug = re.sub(R"[,;].*", "", drug) # Ignore text behind commas and semicolons
        
        drug_std = DRUGDICT.get(drug)
        if drug_std: # First check if there's a specific entry for it (including a combination drug definition)
            standardized_druglist.append(drug_std)
            continue            
        elif "/" in drug: # For combination drugs, will look up each component separately
            # To add combination drug, only need to add standardized components and their combination joined by "/" in any order
            comps = drug.split("/")
            comp1 = DRUGDICT.get(comps[0])
            if not comp1: # Try fuzzylookup if not in keys
                comp1 = find_closest_string(comps[0], DRUGDICT.keys(), thresh=thresh)
            comp2 = DRUGDICT.get(comps[1])
            if not comp2: # Try fuzzylookup if not in keys
                comp2 = find_closest_string(comps[1], DRUGDICT.keys(), thresh=thresh)
            if comp1 and comp2: # If both components can be standaridized (either via key or fuzzy)
                original = DRUGDICT.get(F"{comp1}/{comp2}")
                rearranged = DRUGDICT.get(F"{comp2}/{comp1}")
                if original:
                    standardized_druglist.append(original)
                    continue
                elif rearranged:
                    standardized_druglist.append(rearranged)
                    continue
                else: # If at this point, neither conformation has worked
                    comps_std = [comp1, comp2]
                    comps_std.sort() # Standardize component order by alphabetical order 
                    standardized_druglist.append("/".join(comps_std)) # Append empty string 
                    continue
        else: # Attempt fuzzy matching on whole string
            close_match = find_closest_string(drug, DRUGDICT.keys(), thresh=thresh)
            close_match = DRUGDICT.get(close_match)
            standardized_druglist.append(close_match)
    if not standardized_druglist: # If list is empty (usually b/c no str in list)
        standardized_druglist.append(None) # Append None item so that list has at least 1 item
    return standardized_druglist

if __name__ == "__main__":
    import time 
    start_time = time.time()
    # print(standardize(["aspiren (oral)"]))
    # print(standardize(["aspir9n (oral)"]))
    # print(standardize(["CHLORDIAZEPOXIDE/CLIDINIUM"])) # "CHLORDIAZEPOXIDE/CLIDINIUM"
    # print(standardize(["LIBRAX/CHLORDIAZEPXIDE"])) # "CHLORDIAZEPOXIDE/CLIDINIUM"
    # print(standardize(["estrogen/testosterone"])) # 'ESTROGENS/TESTOSTERONE'
    # print(standardize(["t3stosterone/estrogen"])) # 'ESTROGENS/TESTOSTERONE'
    print(standardize(["Dipyridamole, oral short acting"])) #
    print(standardize(["phenytoin"])) #
    
    print("--- %s seconds ---" % (time.time() - start_time))
