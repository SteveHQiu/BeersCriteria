import kivy
from kivy.app import App
from kivy.uix.label import Label # Imports Label element
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
# from kivy.uix.widget import Widget
# from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
# from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.treeview import TreeView, TreeViewLabel

# from kivy.config import Config
# Config.set('graphics', 'width', '70')
# Config.set('graphics', 'height', '150')

# from kivy.core.window import Window
# Window.size = (300, 500)

# Test
# Internals 
import drugstd
from check_drug import checkDrug, checkInterac



class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs) # Calls the superconstructor 
        self.cur_text = ""
    
    def checkBeers(self):
        tree_view: TreeView = self.ids.tree_view
        scroll_view: ScrollView = self.ids.scroll_view # Use element with "accordion" id (doesn't need to be bound) to assign ScrollView object
        text_in: str = self.text_in1.text
        delimiters = ["\n", ",", ";"]
        drugs = [text_in]
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
            drug_warning = checkDrug(drug, std=False)
            if drug_warning:
                l1_node = tree_view.add_node(TreeViewLabel(text=f"Potential issues with {drug}"))
                tree_view.add_node(TreeViewLabel(text=f"{drug_warning}", markup=True), l1_node)
        # Interaction reporting
        for offending_drugs, report in checkInterac(drugs_std, std=False):
            l1_node = tree_view.add_node(TreeViewLabel(text=f"Interaction between {offending_drugs}"))
            tree_view.add_node(TreeViewLabel(text=f"{report}", markup=True), l1_node)
        
    def testFx(self):
        obj: TreeView = self.ids.tree_view
        print(obj.height)
        

class WrappedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding_x = 10
        self.bind(width=lambda *x: self.setter('text_size')(self, (self.width, None)), 
                texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))
        # Binds the changes in one property to the setter of another property such that every time kivy tries to change the anchor property, it will also pass the new property value (or some aspect of it) to the setter of the linked property




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
