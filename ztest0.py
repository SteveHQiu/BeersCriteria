import enum, re
from typing import Hashable
import pandas as pd
import json, csv
from pandas import DataFrame
import timeit

#%%
print(bool([[]]))
#%%
if 0:
    counterion = "ACETATE"
    drug_dict = {"ACETOACETATE": 1, "SOMETHING1 ACETATE": 2, "ACETATE SOMETHING2": 3, "ACETATES": 4, "SOMETHING1": 99} # For testing

    def _addDictEntry(d: dict, entry: dict):
            entry = {k: entry[k] for k in entry if k not in d} # Get non-overlapping entries
            d.update(entry)
            
    for key in drug_dict.copy():
        val = drug_dict[key]
        matches = re.findall(RF"(?:\W|^){counterion}(?:\W|$)", key) # Find counterion at beginning or end, need normal brackets since braces will result in literal interpretation
        if matches:
            del drug_dict[key]
            for match in matches:
                print(match + " | " + key)
                key = key.replace(match, "")
            _addDictEntry(drug_dict, {key: val}) # Only adds to dict if no conflict, modifies in-inplace

    print(drug_dict)

#%% Adding to dicts
if 0:
    def addDictEntry(d: dict, entry: dict):
        entry = {k: entry[k] for k in entry if k not in d} # Get non-overlapping entries
        d.update(entry)

    a = {"a": 1, "b":2, "c":3}
    b = {"a": 69, "e": 10}
    addDictEntry(a, b)
    print(a)
    del a["a"]
    print(a)

#%% Checking inequalities
if 0:
    import re
    from re import Match

    def checkIneq(rules_str: str, num) -> bool:
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
            
    # print(checkIneq(">134.4, <150 , 120-1400", 134.5))
    # print(checkIneq("=134.5", 134.5))
    # print(checkIneq("=1.1", 1.1))
    # print(checkIneq("=2", 2))
    print(checkIneq("<=80", 90))
    print(checkIneq(">=80", 90))
    print(checkIneq("<=80", 30))
    print(checkIneq(">=80", 30))


#%% Budget dataframe
if 0:
    class CDataFrame:
        def __init__(self, df_dict: dict[str, list] = dict(), csv_path = "") -> None:
            if csv_path:
                with open(csv_path, "r", encoding="utf-8-sig") as file: # utf-8-sig to strip off weird characters at beginning of csv
                    csv_reader = csv.reader(file)
                    csv_rows: list[list[str]] = [row for row in csv_reader]
                cols = csv_rows[0] # First row as columns
                self.columns = {col: ind for ind, col in enumerate(cols)} # Map cols to index
                self.rows = [row for row in csv_rows[1:] if any(row)] # Get rest of rows, filter out empty rows
            elif df_dict: # Unpack into DF
                self.columns = {col: ind for ind, col in enumerate(df_dict)}
                max_len = max([len(val) for val in df_dict.values()])
                recons_df: list[list] = []
                for i in range(max_len):
                    entry = []
                    for col_key in self.columns:
                        col_vals = df_dict[col_key]
                        entry.append(col_vals[i]) # Append col val corresponding to row
                    recons_df.append(entry)
                self.rows = recons_df
            else:
                self.columns = []
                self.rows = []
        
        def __getitem__(self, key: str):
            ind = self.columns[key] # Convert column label to index
            return [row[ind] for row in self.rows]
        
        def __setitem__(self, key: str, values: list):
            ind = self.columns[key]
            if type(values) == list:
                for i, row in enumerate(self.rows):
                    row[ind] = values[i]
            else: # Assume values is scalar
                for i, row in enumerate(self.rows):
                    row[ind] = values
        
        def __len__(self):
            return len(self.rows) # Gets number of entries/rows
        
        def read_csv(self, csv_path):
                with open(csv_path, "r", encoding="utf-8-sig") as file: # utf-8-sig to strip off weird characters at beginning of csv
                    csv_reader = csv.reader(file)
                    csv_rows: list[list[str]] = [row for row in csv_reader]
                cols = csv_rows[0] # First row as columns
                self.columns = {col: ind for ind, col in enumerate(cols)} # Map cols to index
                self.rows = [row for row in csv_rows[1:] if any(row)] # Get rest of rows, filter out empty rows
        
        def findRows(self, col, match):
            ind = self.columns[col]
            cdf = CDataFrame()
            cdf.columns = self.columns.copy() # Copy over columns dict
            for row in self.rows:
                row_value = row[ind]
                if row_value == match:
                    cdf.rows.append(row)
            return cdf # Return new dataframe with matches
            
        
        def iterrows(self):
            for ind, row in enumerate(self.rows):
                cdf = CDataFrame()
                cdf.columns = self.columns.copy() # Copy over columns dict
                cdf.rows.append(row)
                yield (ind, cdf) # Yield each row as a df

    # a = CDataFrame(csv_path="data/test.csv")
    a = CDataFrame({"Drug": ["drug1", "drug2", "drug3", "drug4"],
                    "Properties": ["prop1", "prop2", "prop3", "prop3"],
                    "Other": ["other2", "other2", "other3", "other4"]})
    DF_I = CDataFrame(csv_path=R"data\interac_std.csv")
    DF_S = CDataFrame(csv_path=R"data\screen_std.csv")
    import pickle
    with open("screen_std.dat", "w+b") as file:
        pickle.dump(DF_S, file)

    with open("screen_std.dat", "rb") as file: 
        df = pickle.load(file)
    print(df.columns)

#%% Budget networkx
if 0:
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