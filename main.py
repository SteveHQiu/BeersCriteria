import pickle, json, time, re, webbrowser, platform
from difflib import SequenceMatcher
from threading import Thread, main_thread, Event
from queue import Queue




from kivymd.app import MDApp
from kivymd.theming import ThemeManager, ThemableBehavior
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, TwoLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField, MDTextFieldRect

from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.popup import Popup

from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivy.clock import Clock


# Internals 
import drugstd
from check_drug import checkDrug, checkInterac
from custom_libs import CDataFrame
from internals import NodeType, RawReportItem

# Windows rendering
if platform.system() == "Windows":
    from kivy.core.window import Window
    Window.size = (400, 650)
    
# Constants
with open("data/drugdict.json", "r") as file:
    DICT: dict = json.load(file)




# Kivy classes
class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs) # Calls the superconstructor 
        
class CPopup(MDDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    pass

class CButton(MDRectangleFlatButton):
    pass

class CScrollView(MDScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.id = "testid"
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
        dict_dist = {i.capitalize(): SequenceMatcher(a=text, b=i).ratio() for i in matches} # Convert labels to lowercase with capitalized first char
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
        app = MDApp.get_running_app()
        main_screen = app.root.ids.screen_beers
        text_input = main_screen.ids.text_in1
        
        if main_screen.ids.text_in1.text: # If the text input is not empty
            text_to_add = f", {btn.text}"
        else: # Assume empty text input
            text_to_add = f"{btn.text}"
        main_screen.ids.text_in1.text += text_to_add
        self.text = ""
        # Function of each buttons ends here 
        
        self.suggestions = []
        for cscrollview in cscrollviews:
            parent_layout.remove_widget(cscrollview)
            
class CTreeView(TreeView):
    def select_node(self, node):
        self.toggle_node(node) 
        # return super().select_node(node)
    pass

class CTreeViewIcon(TreeViewNode, TwoLineIconListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def changeIcon(self, icon): # Workaround to changing icon without instantiating new widget
        self.ids.l_icon.icon = icon
        
    pass

class CTreeViewLabel(TreeViewLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    pass

class DrawerLayout(BoxLayout):
    pass

class MDListDrawer(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        '''Called when tap on a menu item.'''

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color

class ScreenBeers(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.finished_check = Event() # Cross-thread event to indicate whether or not drug checking has finished
        self.reports_queue = Queue() # Queue for nodes to be added 
        
    def checkBeers(self):
        # Note that graphics will not update until this function reaches return statement/end of fx definition        


        tree_view: CTreeView = self.ids.tree_view
        for node in [i for i in tree_view.iterate_all_nodes()]:
            tree_view.remove_node(node) # Clear nodes   
        
        creat_str: str = self.ids.creatinine.text
        try: 
            creat_num = float(creat_str)
        except ValueError: # Set creat_num to 0 when creat_str is empty or invalid
            creat_num = 0
        
        text_in: str = self.ids.text_in1.text
        
        # Reset event and queues
        self.finished_check = Event() # Cross-thread event to indicate whether or not drug checking has finished
        self.reports_queue = Queue() # Queue for nodes to be added 
        
        thread_checking = Thread(target=self.parseDrugs, args=[creat_num, text_in]) 
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
        self.pop_up = CPopup()
        self.pop_up.open()
        print("========= Show loading ===========")
    
    def _changeGraphics(self, dt, *args): # dt = time between scheduling and calling of function
        
        while True:
            while not self.reports_queue.empty():
                item: RawReportItem = self.reports_queue.get()
                self._addReportItem(item) # Add these nodes using the main thread
            if self.finished_check.is_set(): # Waiting on separate thread to finish 
                self.pop_up.dismiss() # Backup pop-up dismisser in case separate thread does not handle it 
                break
            time.sleep(0.01) # In case other threads need to run extensive loops 
        
    def _addReportItem(self, rep_item: RawReportItem): # Passing processed information into main thread
        tree_view: CTreeView = self.ids.tree_view
        
        def _genItem(item: RawReportItem, parent_item = None):
            # Need internal fxn to separate self object from recursion of tree nodes
            if item.node_type == NodeType.ICON:
                tree_icon = CTreeViewIcon(text=item.text, secondary_text=item.secondary)
                tree_icon.changeIcon(item.icon)
                
                cur_node = tree_view.add_node(tree_icon, parent_item) # If parent_item == None, will add to root

                
            elif item.node_type == NodeType.LABEL:
                cur_node = tree_view.add_node(CTreeViewLabel(text=item.text, markup=True), parent_item)
            
            if item.children:
                for l2_item in item.children:
                    _genItem(l2_item, cur_node)
        
        _genItem(rep_item)
            


    
    def parseDrugs(self, creat_num: float, text_in: str):
        # Connected to self.finished_check and self.reports_queue for multi-threading
        
        drugs = re.split("\n|,|;", text_in) # Split by delimiters
        drugs = [d.strip() for d in drugs if d.strip()]
        print("Input texts: ", drugs)
        drugs_std = [drugstd.standardize([d])[0] for d in drugs]
        drugs_std = [d for d in drugs_std if d] # Filter empty data types
        drugs_std = list(set(drugs_std)) # Screen out duplicates
        print("Standardized: ", drugs_std)
        
        

        if len(drugs_std) == 0:
            pill_icon = "pill-off"
            prim_text = f"No standardized drugs found"
            sec_text = F"Drug names may be misspelled"
            sub_item = RawReportItem(
                text=f"No standardized drugs have been found after checking the input against our database. Drug names may be misspelled. The 'Standardized drug name lookup' input box above can be used to search for drug entries present in the database",
                node_type=NodeType.LABEL,
            )

        elif len(drugs_std) >= 1:
            pill_icon = "pill-multiple"
            prim_text = f"{len(drugs_std)} standardized drugs found"
            if len(drugs_std) == 1:
                prim_text = f"1 standardized drug found"
                pill_icon = "pill"
                
            sec_text = ", ".join([d.capitalize() for d in drugs_std])  # Join drug names after capitalizing
            sub_item = RawReportItem(
                text=sec_text,
                node_type=NodeType.LABEL,
            )
            

        raw_report_item = RawReportItem(
            text=prim_text,
            secondary=sec_text,
            icon=pill_icon,
            children=[sub_item],
            node_type=NodeType.ICON,
        )
        
        self.reports_queue.put(raw_report_item)
        
        report_items = 0
        # Drug screening
        for drug in drugs_std:
            drug_warnings = checkDrug(drug, creat_num=creat_num, std=False)
            if drug_warnings:
                report_items += 1
                self.reports_queue.put(drug_warnings)
        # Interaction reporting
        for drug_interac in checkInterac(drugs_std, std=False):
            report_items += 1
            self.reports_queue.put(drug_interac)
        
        # Check if drugs present but no report items
        if report_items == 0 and len(drugs_std) >= 1:
            sub_item = RawReportItem(
                text=f"No medications of concern related the Beers Criteria guidlines have been detected after checking input against our database. However, other interactions/concerns aside from those listed in the Beers Criteria may still exist. For more general interaction checkers, please see the links in the 'Other Resources' tab",
                node_type=NodeType.LABEL,
            )
            none_item = RawReportItem(
                text=f"No medications of concern found",
                secondary=F"Med list is OK from Beers Criteria perspective",
                icon="check",
                children=[sub_item],
                node_type=NodeType.ICON,
            )
            self.reports_queue.put(none_item)

        # Refer back to self events and popups to dismiss them
        self.finished_check.set()
        self.pop_up.dismiss()
    pass

class ScreenResources(Screen):
    pass

class ScreenInfo(Screen):
    pass


class BeersApp(MDApp):
    """
    This class inherits the App class from kivy
    The name of this class will also determine the name of the .kv files (for layout/design)
    .kv file name is not case-sensitive to the class name but should be all lowercase to avoid issues
    .kv file name can exclude "App" portion of App class identifier
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
    
    def drawNavigation(self):
        self.root.ids.nav_drawer.set_state('open')
        return
    
    def openLink(self, link):
        webbrowser.open(link)

    
    # def build(self): # Returns the UI
        # root = RootLayout()
    #     return root # Return whatever root element you are using for the UI
        


app_instance = BeersApp() # Creates instance of the app
app_instance.run() # Runs the instance of the app 
