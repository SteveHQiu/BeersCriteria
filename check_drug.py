import json
import pandas as pd
from pandas import DataFrame
from itertools import combinations, permutations
import networkx as nx
from networkx.algorithms.bipartite.matching import hopcroft_karp_matching

import drugstandards

DF_S = pd.read_csv(R"data\screen_std.csv")
DF_I = pd.read_csv(R"data\interac_std.csv")

def checkDrug(drug: str, std = True):
    global DF_S    
    if std:
        drug = drugstandards.standardize([drug])[0]
    if drug in list(DF_S["ExStandardized"]):
        entry = DF_S.loc[DF_S["ExStandardized"] == drug] # Take first item
        entry = entry.reset_index(drop=True) # Reset index to access by labels rather than relative positions
        print(f"Found {len(entry)} entries")
        if len(entry) > 1:
            print(entry.nunique())
        drug_origin = entry.at[0, "Drug"]
        rec = entry.at[0, "Recommendation"]
        rationale = entry.at[0, "Rationale"]
        report = f"Beers entry: {drug_origin}\nRecommendation: {rec}\nRationale: {rationale}"
        return report
    return ""

def checkInterac(drugs: list[str], std = True):
    global DF_I
    report = ""
    if std:
        drugs = [drugstandards.standardize([d])[0] for d in drugs]
        drugs = [d for d in drugs if d] # Filter empty data types
    if len(drugs) > 1:        
        for index, row in DF_I.iterrows():
            cols = ["Drug 1", "Drug 2", "Drug 3"]
            cols = [col for col in cols if type(row[col]) == str] # Default cell value is float of nan, only parse strings 
            graph = nx.Graph()
            graph.add_nodes_from(cols, bipartite=0)
            graph.add_nodes_from(drugs, bipartite=1)
            for drug_cat in cols:
                members_str: str = row[drug_cat]
                members: list[str] = json.loads(members_str)
                for drug in drugs:
                    drug = drug.upper()
                    if drug in members: # If there is membership, it hasn't been tracked already, and the category has not already been satisfied
                        graph.add_edge(drug_cat, drug)
            max_match = hopcroft_karp_matching(graph, cols)
            if len(max_match)/2 >= len(cols): # Divide by 2 since max match output is undirected
                drug_origin = {m: max_match[m] for m in max_match if "Drug" in m} # Filter for mappings with drug categories as key
                rec = row["Recommendation"]
                rationale = row["Risk Rationale"]
                rule_report = f"Drugs: {drug_origin}\nRecommendation: {rec}\nRationale: {rationale}\n---------------\n"
                report += rule_report
        # Can probably solve this more efficiently with Hall's theorem via graphs
    if report:
        return report
    return "No interactions to report"

if __name__ == "__main__":
    print(checkInterac(["Losartan", "Trandolapril"])) # Yes
    # checkInterac(["Trandolapril", "Losartan"]) # Yes
    # checkInterac(["Losartan", "Losartan"]) # No
    # checkInterac(["Triamterene", "Losartan"]) # Yes
    # checkInterac(["Losartan", "Quazepam", "Quazepam"]) # No
    # checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Trospium"]) # No
    # checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Prochlorperazine"]) # Yes
    # checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin"]) # No
    # checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin", "Lacosamide"]) # Yes