import json, collections, itertools
from typing import Hashable

import pandas as pd


import drugstd

DF_S = pd.read_csv(R"data\screen_std.csv")
DF_I = pd.read_csv(R"data\interac_std.csv")
INFINITY = float("inf")

def checkDrug(drug: str, std = True):
    global DF_S    
    if std:
        drug = drugstd.standardize([drug])[0]
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
    interactions: list[tuple[str, str]] = []
    if std:
        drugs = [drugstd.standardize([d])[0] for d in drugs]
        drugs = [d for d in drugs if d] # Filter empty data types
    if len(drugs) > 1:        
        for index, row in DF_I.iterrows():
            cols = ["Drug 1", "Drug 2", "Drug 3"]
            cols = [col for col in cols if type(row[col]) == str] # Default cell value is float of nan, only parse strings 
            
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
                rule_report = f"Drugs: {drug_origin}\nRecommendation: {rec}\nRationale: {rationale}"
                interactions.append((str(offending_drugs), rule_report))
    return interactions

class CGraph:
    def __init__(self) -> None:
        self.data: dict[Hashable, set[Hashable]] = {"a": {"b"}, "b": {"a"}}
        self.set1: set[Hashable] = set()
        self.set2: set[Hashable] = set()
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def add_nodes_from(self, nodes: list[Hashable], bipartite=-1):
        for node in nodes:
            self.add_node(node, bipartite=bipartite)
    
    def add_node(self, node: Hashable, bipartite=-1):
        self.data[node] = set()
        if bipartite == 0:
            self.set1.add(node)
        if bipartite == 1:
            self.set2.add(node)
        return node
    
    def add_edge(self, u_of_edge: Hashable, v_of_edge: Hashable):
        if u_of_edge not in self.data:
            self.data[u_of_edge] = set()
        if v_of_edge not in self.data:
            self.data[v_of_edge] = set()
        self.data[u_of_edge].add(v_of_edge)
        self.data[v_of_edge].add(u_of_edge)
    
    def bipartite_sets(self):
        return (self.set1, self.set2)


def hopcroft_karp_matching(G: CGraph, *args):
    # First we define some auxiliary search functions.
    #
    # If you are a human reading these auxiliary search functions, the "global"
    # variables `leftmatches`, `rightmatches`, `distances`, etc. are defined
    # below the functions, so that they are initialized close to the initial
    # invocation of the search functions.
    def breadth_first_search():
        for v in left:
            if leftmatches[v] is None:
                distances[v] = 0
                queue.append(v)
            else:
                distances[v] = INFINITY
        distances[None] = INFINITY
        while queue:
            v = queue.popleft()
            if distances[v] < distances[None]:
                for u in G[v]:
                    if distances[rightmatches[u]] is INFINITY:
                        distances[rightmatches[u]] = distances[v] + 1
                        queue.append(rightmatches[u])
        return distances[None] is not INFINITY

    def depth_first_search(v):
        if v is not None:
            for u in G[v]:
                if distances[rightmatches[u]] == distances[v] + 1:
                    if depth_first_search(rightmatches[u]):
                        rightmatches[u] = v
                        leftmatches[v] = u
                        return True
            distances[v] = INFINITY
            return False
        return True

    # Initialize the "global" variables that maintain state during the search.
    left, right = G.bipartite_sets()
    leftmatches = {v: None for v in left}
    rightmatches = {v: None for v in right}
    distances = {}
    queue = collections.deque()

    # Implementation note: this counter is incremented as pairs are matched but
    # it is currently not used elsewhere in the computation.
    num_matched_pairs = 0
    while breadth_first_search():
        for v in left:
            if leftmatches[v] is None:
                if depth_first_search(v):
                    num_matched_pairs += 1

    # Strip the entries matched to `None`.
    leftmatches = {k: v for k, v in leftmatches.items() if v is not None}
    rightmatches = {k: v for k, v in rightmatches.items() if v is not None}

    # At this point, the left matches and the right matches are inverses of one
    # another. In other words,
    #
    #     leftmatches == {v, k for k, v in rightmatches.items()}
    #
    # Finally, we combine both the left matches and right matches.
    return dict(itertools.chain(leftmatches.items(), rightmatches.items()))


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