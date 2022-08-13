import json, re, operator
from difflib import SequenceMatcher
# import Levenshtein

    
with open("data/drugdict.json", "r") as file:
    DRUGDICT: dict = json.load(file)

  
def find_closest_string(query, dictionary, thresh=0.85):
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


def standardize(druglist, thresh=0.85):
    """ This function takes a list of drugs (brand name,
        misspelled drugs, generic names) and converts them
        to the generic names. It is used to provide naming
        consistency to the FAERS reports.
    """
    standardized_druglist = []
    for drug in druglist:
        drug = drug.upper()
        gen = DRUGDICT.get(drug)
        if gen:
            standardized_druglist.append(gen)
            continue
        else:
            close_match = find_closest_string(str(drug), DRUGDICT.keys(), thresh=thresh)
            close_match = DRUGDICT.get(close_match)
            standardized_druglist.append(close_match)
    return standardized_druglist

if __name__ == "__main__":
    import time 
    start_time = time.time()
    print(standardize(["aspiren"]))
    print(standardize(["test"]))
    print("--- %s seconds ---" % (time.time() - start_time))
