import pickle, json, time, re
from difflib import SequenceMatcher
from threading import Thread, main_thread, Event
from queue import Queue

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
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.clock import Clock

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
        
class PopupBox(Popup):
    pass

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
        if not text: # If text empty, update suggestions and remove box
            parent_layout: BoxLayout = self.parent
            cscrollviews = [l for l in parent_layout.children if type(l) == CScrollView]
            self.suggestions = []
            for cscrollview in cscrollviews:
                parent_layout.remove_widget(cscrollview)
            return
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.finished_check = Event() # Cross-thread event to indicate whether or not drug checking has finished
        self.reports_queue = Queue() # Queue for nodes to be added 
    
    
    def checkBeers(self):
        # Note that graphics will not update until this function reaches return statement/end of fx definition        
        
        tree_view: TreeView = self.root.ids.tree_view
        for node in [i for i in tree_view.iterate_all_nodes()]:
            tree_view.remove_node(node) # Clear nodes        
        creat_str = self.root.ids.creatinine.text
        try: 
            creat_num = float(creat_str)
        except ValueError: # Set creat_num to 0 when creat_str is empty or invalid
            creat_num = 0
        
        text_in: str = self.root.text_in1.text
        
        # Reset event and queues
        self.finished_check = Event() # Cross-thread event to indicate whether or not drug checking has finished
        self.reports_queue = Queue() # Queue for nodes to be added 
        
        thread_checking = Thread(target=self._checkDrugs, args=[creat_num, text_in]) 
        # Separate thread can't change kivy graphics, need to pass info into main thread
        # Passing Queue container to share nodes to be generated since they can only be rendered in main thread
        thread_checking.daemon = True
        thread_checking.start()
        self._renderQueueNodes() # Passes listening of queue to a different delayed action so that this main function can be returned and graphics can be updated


    def _renderQueueNodes(self, *args): # Extra args can be passed down to the changGraphics fx 
        self._showLoading() # Open "loading" popup
        Clock.schedule_once(lambda dt: self._changeGraphics(dt, *args), 0) # Schedule action for when graphics can update, dt is automatically passed in as the time b/n scheduling and calling of function
        # Passing _changeGraphics off to scheduled action allows kivy to consider the main function to be finished hence graphics can be updated
        
    def _showLoading(self):
        self.pop_up = PopupBox(title='Please wait...', content=Label(text='Checking drugs against database'), size_hint=(0.4, 0.2),
              auto_dismiss=False)
        self.pop_up.open()
        print("========= Show loading ===========")
    
    def _changeGraphics(self, dt, *args): # dt = time between scheduling and calling of function
        
        while True:
            while not self.reports_queue.empty():
                nodes: tuple[str, str] = self.reports_queue.get()
                self._addNestedNode(nodes[0], nodes[1]) # Add these nodes using the main thread
            if self.finished_check.is_set(): # Waiting on separate thread to finish 
                break
        
    def _addNestedNode(self, l1_info, l2_info = None): # Passing processed information into main thread
        tree_view: TreeView = self.root.ids.tree_view
        l1_node = tree_view.add_node(TreeViewLabel(text=l1_info))
        if l2_info: # If there's info for subnode
            tree_view.add_node(TreeViewLabel(text=l2_info, markup=True), l1_node)
        
    
    def _checkDrugs(self, creat_num: float, text_in: str):
        # Connected to self.finished_check and self.reports_queue for multi-threading
        
        drugs = re.split("\n|,|;", text_in) # Split by delimiters
        drugs = [d.strip() for d in drugs if d.strip()]
        print("Input texts: ", drugs)
        drugs_std = [drugstd.standardize([d])[0] for d in drugs]
        drugs_std = [d for d in drugs_std if d] # Filter empty data types
        drugs_std = list(set(drugs_std)) # Screen out duplicates
        print("Standardized: ", drugs_std)
        
        
        l1_info = f"{len(drugs_std)} standardized drugs found"
        l2_info = f"{drugs_std}"
        self.reports_queue.put((l1_info, l2_info))
        
        # Drug screening
        for drug in drugs_std:
            drug_warning = checkDrug(drug, creat_num=creat_num, std=False)
            if drug_warning:
                l1_info = f"Potential issues with {drug}"
                l2_info = f"{drug_warning}"
                self.reports_queue.put((l1_info, l2_info))
        # Interaction reporting
        for offending_drugs, report in checkInterac(drugs_std, std=False):
            l1_info = f"Interaction between {offending_drugs}"
            l2_info = f"{report}"
            self.reports_queue.put((l1_info, l2_info))
        
        # Refer back to self events and popups to dismiss them
        self.finished_check.set()
        self.pop_up.dismiss()
        
    
    
    # def build(self): # Returns the UI
    #     root = RootLayout()
    #     return root # Return whatever root element you are using for the UI
        


app_instance = BeersApp() # Creates instance of the app
app_instance.run() # Runs the instance of the app 
