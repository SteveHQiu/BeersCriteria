import json, pickle, re
from re import Match

import drugstd
from custom_libs import CGraph, hopcroft_karp_matching, CDataFrame

# Serialize files (Uncomment to export new .dat files On PC)
with open("data/screen_std.dat", "w+b") as file:
    DF_S = CDataFrame(csv_path="data/screen_std.csv")
    pickle.dump(DF_S, file)

with open("data/interac_std.dat", "w+b") as file:
    DF_I = CDataFrame(csv_path="data/interac_std.csv")
    pickle.dump(DF_I, file)
    
# Load (Uncomment for loading of generated .dat files on mobile)
with open("data/screen_std.dat", "rb") as file:
    DF_S: CDataFrame = pickle.load(file)

with open("data/interac_std.dat", "rb") as file:
    DF_I: CDataFrame = pickle.load(file)

INFINITY = float("inf")

def checkDrug(drug: str, creat_num: float = 0, std = True):
    if std:
        drug = drugstd.standardize([drug])[0]
    if drug in DF_S["ExStandardized"]:
        entry = DF_S.findRows("ExStandardized", drug) # Take first item
        print(f"Found {len(entry)} entries")
        creat_num = creat_num
        report = ""
        for ind, row in entry.iterrows():
            row_report = ""
            drug_origin = row["Drug"]
            rec = row["Recommendation"]
            rationale = row["Rationale"]
            condition = row["Condition"]
            creat_rule = row["Creatinine Clearance"]
            
            if drug_origin and type(drug_origin) == str:
                row_report += f"[b]Drug[/b]: {drug_origin}\n"
            if condition and type(condition) == str:
                row_report += f"[b]Condition[/b]: {condition}\n"
            if creat_rule and type(creat_rule) == str:
                row_report += f"[b]Creatinine clearance threshold (mL/min)[/b]: {creat_rule}\n"
            if rec and type(rec) == str:
                row_report += f"[b]Recommendation[/b]: {rec}\n"
            if rationale and type(rationale) == str:
                row_report += f"[b]Rationale[/b]: {rationale}\n"
            row_report += "[b]====================[/b]\n\n"
            
            if creat_num and creat_rule: # If creatinine number and rule are present, check number against the rule
                if not _checkIneq(creat_rule, creat_num):
                    row_report = "" # Clear row report for this rule if it doesn't meet requirements
            
            report += row_report
            
        return report
    return ""

def _checkIneq(rules_str: str, num) -> bool:
    # Check inequality string against a number
    rules = [r.strip() for r in rules_str.split(",") if r.strip()] # Obtain non-empty strings
    checks = []
    for rule in rules:
        eq: Match = re.search(R"(?<!<|>)=(\d+\.?\d*)", rules_str) # Capture floats and negative lookbehind so it doesn't match ge or le 
        gt: Match = re.search(R">(\d+\.?\d*)", rules_str)
        lt: Match = re.search(R"<(\d+\.?\d*)", rules_str)
        ge: Match = re.search(R">=(\d+\.?\d*)", rules_str)
        le: Match = re.search(R"<=(\d+\.?\d*)", rules_str)
        rg: Match = re.search(R"(\d+\.?\d*)\-(\d+\.?\d*)", rules_str)
        # Equals
        # Greater
        if eq:
            num_eq = float(eq.group(1))
            checks.append(num == num_eq)
        if gt:
            num_eq = float(gt.group(1))
            checks.append(num > num_eq)
        if lt:
            num_eq = float(lt.group(1))
            checks.append(num < num_eq)
        if ge:
            num_eq = float(ge.group(1))
            checks.append(num >= num_eq)
        if le:
            num_eq = float(le.group(1))
            checks.append(num <= num_eq)
        if rg:
            num_low = float(rg.group(1))
            num_high = float(rg.group(2))
            if num_low < num_high:
                checks.append(num_low <= num <= num_high)
            else: # Otherwise assume they are reversed
                checks.append(num_low >= num >= num_high)
    return all(checks) # Only return true if all rules are satisfied

def checkInterac(drugs: list[str], std = True):
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
    # print(checkInterac(["Losartan", "Trandolapril"])) # Yes
    # print(checkInterac(["Trandolapril", "Losartan"])) # Yes
    # print(checkInterac(["Losartan", "Losartan"])) # No
    # print(checkInterac(["Triamterene", "Losartan"])) # Yes
    # print(checkInterac(["TRIMETHOPRIM/SULFAMETHOXAZOLE", "Phenytoin", "Quazepam"])) # Yes
    # print(checkInterac(["Losartan", "Quazepam", "Quazepam"])) # No
    # print(checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Trospium"])) # No
    # print(checkInterac(["Losartan", "Quazepam", "Quazepam", "Trospium", "Prochlorperazine"])) # Yes
    # print(checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin"])) # No
    # print(checkInterac(["Losartan", "Gabapentin", "Gabapentin", "Pregabalin", "Lacosamide"])) # Yes
    # print(checkDrug("Levetiractam", creat_num=90))
    print(checkDrug("ENOXAPARIN", creat_num=6))
