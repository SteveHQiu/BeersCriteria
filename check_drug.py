import json

import drugstd
from custom_libs import CGraph, hopcroft_karp_matching, CDataFrame

DF_S = CDataFrame(csv_path=R"data\screen_std.csv")
DF_I = CDataFrame(csv_path=R"data\interac_std.csv")

INFINITY = float("inf")

def checkDrug(drug: str, std = True):
    global DF_S    
    if std:
        drug = drugstd.standardize([drug])[0]
    if drug in DF_S["ExStandardized"]:
        entry = DF_S.findRows("ExStandardized", drug) # Take first item
        print(f"Found {len(entry)} entries")
        report = ""
        for ind, row in entry.iterrows():
            drug_origin = row["Drug"]
            rec = row["Recommendation"]
            rationale = row["Rationale"]
            condition = row["Condition"]
            creatinine = row["Creatinine Clearance"]
            if drug_origin and type(drug_origin) == str:
                report += f"[b]Drug[/b]: {drug_origin}\n"
            if condition and type(condition) == str:
                report += f"[b]Condition[/b]: {condition}\n"
            if creatinine and type(creatinine) == str:
                report += f"[b]Creatinine clearance threshold[/b]: {creatinine}\n"
            if rec and type(rec) == str:
                report += f"[b]Recommendation[/b]: {rec}\n"
            if rationale and type(rationale) == str:
                report += f"[b]Rationale[/b]: {rationale}\n"
            report += "[b]====================[/b]\n\n"
        return report
    return ""

def checkInterac(drugs: list[str], std = True):
    global DF_I
    interactions: list[tuple[str, str]] = []
    if std:
        drugs = [drugstd.standardize([d])[0] for d in drugs]
        drugs = [d for d in drugs if d] # Filter empty data types
    if len(drugs) > 1:        
        for index, row in DF_I.iterrows():
            cols = ["Drug 1", "Drug 2", "Drug 3"]
            cols = [col for col in cols if row[col] and type(row[col]) == str] # Filter for non-empty strings
            
            graph = CGraph()
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
                drug_origin: dict[str, str] = {m: max_match[m] for m in max_match if "Drug" in m} # Filter for mappings with drug categories as key
                offending_drugs: list[str] = [drug_origin[k] for k in drug_origin]
                rec = row["Recommendation"]
                rationale = row["Risk Rationale"]
                rule_report = f"[b]Drugs[/b]: {drug_origin}\n[b]Recommendation[/b]: {rec}\n[b]Rationale[/b]: {rationale}"
                interactions.append((str(offending_drugs), rule_report))
    return interactions




if __name__ == "__main__":
    print(checkInterac(["Losartan", "Trandolapril"])) # Yes
    print(checkInterac(["Trandolapril", "Losartan"])) # Yes
    print(checkInterac(["Losartan", "Losartan"])) # No
    print(checkInterac(["Triamterene", "Losartan"])) # Yes
    print(checkInterac(["Losartan", "Quazepam", "Quazepam"])) # No
    print(checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Trospium"])) # No
    print(checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Prochlorperazine"])) # Yes
    print(checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin"])) # No
    print(checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin", "Lacosamide"])) # Yes