from typing import Hashable
import pandas as pd
import json
from pandas import DataFrame
import timeit
#%%
import networkx as nx


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

G = nx.Graph()
G.add_edge("a", "b")
G.add_edge("c", "b")
G.add_edge("d", "e")
print(list(G.nodes))
print(G["b"])

G = CGraph()
G.add_edge("a", "b")
G.add_edge("c", "b")
G.add_edge("d", "e")
print(G["b"])


#%%
if 0:
    text_in = "test, lmao\neyy, bar, also foo; test2"
    delimiters = ["\n", ",", ";"]
    drugs = [text_in]
    for delim in delimiters:
        drugs = [txt.split(delim) for txt in drugs]
        drugs = sum(drugs, []) # flatten list
    print(drugs)

#%% Partials
if 0:
    from functools import partial
    fx = partial(int, base=2)
    a = lambda *x: fx("10101")
    print(a)
    print(a("asdfads"))
#%%
if 0:
    from check_drug import checkInterac
    items = ["LMAODRUG1"]
    print(len(items))
    start = timeit.default_timer()
    print(checkInterac(items))
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