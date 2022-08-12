import pickle, json
from difflib import SequenceMatcher

import kivy
from kivy.app import App
from kivy.uix.label import Label # Imports Label element
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.factory import Factory

# from kivy.config import Config
# Config.set('graphics', 'width', '70')
# Config.set('graphics', 'height', '150')

# from kivy.core.window import Window
# Window.size = (300, 500)

# Test
# Internals 
import drugstd
from check_drug import checkDrug, checkInterac
from custom_libs import CDataFrame

with open("data/drugdict.json", "r") as file:
    DICT: dict = json.load(file)

class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs) # Calls the superconstructor 
        self.cur_text = ""
    
    def checkBeers(self):
        tree_view: TreeView = self.ids.tree_view
        scroll_view: ScrollView = self.ids.scroll_view # Use element with "accordion" id (doesn't need to be bound) to assign ScrollView object
        
        creat_str = self.ids.creatinine.text
        try: 
            creat_num = float(creat_str)
        except ValueError: # Set creat_num to 0 when creat_str is empty or invalid
            creat_num = 0
        
        text_in: str = self.text_in1.text
        drugs = [text_in]
        
        delimiters = ["\n", ",", ";"]
        for delim in delimiters:
            drugs = [txt.split(delim) for txt in drugs]
            drugs = sum(drugs, []) # flatten list
        print("Input texts: ", drugs)
        drugs_std = [drugstd.standardize([d])[0] for d in drugs]
        drugs_std = [d for d in drugs_std if d] # Filter empty data types
        drugs_std = list(set(drugs_std)) # Screen out duplicates
        print("Standardized: ", drugs_std)
        
        for node in [i for i in tree_view.iterate_all_nodes()]:
            tree_view.remove_node(node) # Clear nodes
        l1_node = tree_view.add_node(TreeViewLabel(text=f"{len(drugs_std)} standardized drugs found"))
        tree_view.add_node(TreeViewLabel(text=f"{drugs_std}"), l1_node)
        
        # Drug screening
        for drug in drugs_std:
            drug_warning = checkDrug(drug, creat_num=creat_num, std=False)
            if drug_warning:
                l1_node = tree_view.add_node(TreeViewLabel(text=f"Potential issues with {drug}"))
                tree_view.add_node(TreeViewLabel(text=f"{drug_warning}", markup=True), l1_node)
        # Interaction reporting
        for offending_drugs, report in checkInterac(drugs_std, std=False):
            l1_node = tree_view.add_node(TreeViewLabel(text=f"Interaction between {offending_drugs}"))
            tree_view.add_node(TreeViewLabel(text=f"{report}", markup=True), l1_node)
        
    def testFx1(self):
        a = CDataFrame()
    def testFx2(self):
        a = CDataFrame({"col1":["1", "2", "3"], "col2":["1", "2", "3"]})
    def testFx3(self):
        with open("data/screen_std.dat", "rb") as file:
            a = pickle.load(file)
        print(a.columns)
    def testFx4(self):
        with open("data/interac_std.dat", "rb") as file:
            a = pickle.load(file)
        print(a.columns)
        


class CButton(Button):
    pass

class CScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "testid"
    pass

class AutoCompleter(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    suggestions = Factory.ListProperty()
    container = Factory.ObjectProperty()

    def on_text(self, _, text: str):
        text = text.upper()
        matches = []
        for word in DICT:
            if text in word:
                matches.append(word)
        dict_dist = {i: SequenceMatcher(a=text, b=i).ratio() for i in matches}
        list_dist = sorted(dict_dist.items(), key=lambda x: x[1], reverse=True) # Sort by value
        top_matches = list_dist[:5] # Take top 5
        self.suggestions = [i[0] for i in top_matches] # Fetch strs from distance tuples
        
    def on_suggestions(self, _, suggestions): # Runs every time the previously defined suggestions Factory.ListProperty() property updates
        parent_layout: BoxLayout = self.parent
        sibling_nodes: list = list(parent_layout.children)
        widget_index = sibling_nodes.index(self)
        cscrollviews = [l for l in parent_layout.children if type(l) == CScrollView]
        if cscrollviews: # Check if there are already scroll views
            cscrollview = cscrollviews[0] # Take first scrollview 
        else:
            cscrollview = CScrollView()
            parent_layout.add_widget(cscrollview, index=widget_index) # Can add widget with size_hint_y/x: 0 if you want to add to top with index
        container = cscrollview.ids.button_box
        container.clear_widgets()
        if not container: # Safeguard to check if container was instantiated 
            return
        # container.clear_widgets()
        for word in suggestions:
            btn = CButton(text=word,
                on_press=self.select_word,
                size_hint_x=None)
            container.add_widget(btn)
            
    def select_word(self, btn):
        parent_layout: BoxLayout = self.parent
        cscrollviews = [l for l in parent_layout.children if type(l) == CScrollView]
        
        # Function of each button starts here
        app = App.get_running_app()
        if app.root.ids.text_in1.text: # If the text input is not empty
            text_to_add = f", {btn.text}"
        else: # Assume empty text input
            text_to_add = f"{btn.text}"
        app.root.ids.text_in1.text += text_to_add
        self.text = ""
        # Funcction of each buttons ends here 
        
        self.suggestions = []
        for cscrollview in cscrollviews:
            parent_layout.remove_widget(cscrollview)

class BeersApp(App): 
    """
    This class inherits the App class from kivy
    The name of this class will also determine the name of the .kv files (for layout/design)
    .kv file name is not case-sensitive to the class name but should be all lowercase to avoid issues
    .kv file name can exclude "App" portion of App class identifier
    """
    
    def build(self): # Returns the UI
        root = RootLayout()
        return root # Return whatever root element you are using for the UI
        


app_instance = BeersApp() # Creates instance of the app
app_instance.run() # Runs the instance of the app 
