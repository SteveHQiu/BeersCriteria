import collections, itertools, csv
from typing import Hashable

INFINITY = float("inf")

class CGraph:
    def __init__(self) -> None:
        self.data: dict[Hashable, set[Hashable]] = dict()
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
            
    def __len__(self):
        return len(self.rows) # Gets number of entries/rows
    
    def __getitem__(self, key: str):
        ind = self.columns[key] # Convert column label to index
        if len(self) == 1: # For DF with one entry (i.e., a row)
            return self.rows[0][ind] # Get first row, then get corresponding column 
        return [row[ind] for row in self.rows]
    
    def __setitem__(self, key: str, values: list):
        ind = self.columns[key]
        if type(values) == list:
            for i, row in enumerate(self.rows):
                row[ind] = values[i]
        else: # Assume values is scalar
            for i, row in enumerate(self.rows):
                row[ind] = values
    
        
    
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