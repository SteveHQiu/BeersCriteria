import pickle, json, time, re, webbrowser, platform
from difflib import SequenceMatcher
from threading import Thread, main_thread, Event
from queue import Queue
from dataclasses import dataclass


from kivymd.app import MDApp
from kivymd.theming import ThemeManager, ThemableBehavior
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.popup import Popup

from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivy.clock import Clock


# Internals 
import drugstd
from check_drug import checkDrug, checkInterac
from custom_libs import CDataFrame

# Windows rendering
if platform.system() == "Windows":
    from kivy.core.window import Window
    Window.size = (400, 600)
    
# Constants
with open("data/drugdict.json", "r") as file:
    DICT: dict = json.load(file)

# Dataclasses

@dataclass
class RawReportItem:
    """
    Container for strings to be loaded into widgets
    Bridge between calculation thread and rendering main thread
    """
    
    text: str
    secondary: str
    icon: str
    reports: list[str]
    


# Kivy classes
class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs) # Calls the superconstructor 
        
class CPopup(Popup):
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
            
class Report(BoxLayout):
    
    
    # def select_node(self, node):
    #     self.toggle_node(node) 
    #     # return super().select_node(node)
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
        sub_cont = BoxLayout(orientation="vertical")
        sub_item = MDExpansionPanel(
            icon="information",
            content=MDLabel(text="item.reports[0]"),
            panel_cls=MDExpansionPanelTwoLine(
                text="item.text",
                secondary_text="item.secondary"
            )
        )
        sub_cont.add_widget(sub_item)
        report_item = MDExpansionPanel(
            icon="information",
            content=sub_cont,
            panel_cls=MDExpansionPanelTwoLine(
                text="item.text",
                secondary_text="item.secondary"
            )
        )
        self.ids.report.add_widget(report_item)
        
        return

        report_cont: Report = self.ids.report
        report_cont.clear_widgets()
        
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
        
    def _addReportItem(self, item: RawReportItem): # Passing processed information into main thread
        report_item = MDExpansionPanel(
            icon=item.icon,
            content=MDLabel(text=item.reports[0]),
            panel_cls=MDExpansionPanelTwoLine(
                text=item.text,
                secondary_text=item.secondary
            )
        )
        self.ids.report.add_widget(report_item)
        # tree_view: TreeView = self.root.ids.tree_view
        # l1_node = tree_view.add_node(TreeViewLabel(text=l1_info))
        # if l2_info: # If there's info for subnode
        #     tree_view.add_node(TreeViewLabel(text=l2_info, markup=True), l1_node)
        
    
    def parseDrugs(self, creat_num: float, text_in: str):
        # Connected to self.finished_check and self.reports_queue for multi-threading
        
        drugs = re.split("\n|,|;", text_in) # Split by delimiters
        drugs = [d.strip() for d in drugs if d.strip()]
        print("Input texts: ", drugs)
        drugs_std = [drugstd.standardize([d])[0] for d in drugs]
        drugs_std = [d for d in drugs_std if d] # Filter empty data types
        drugs_std = list(set(drugs_std)) # Screen out duplicates
        print("Standardized: ", drugs_std)
        
        
        l2_info = ", ".join([d.capitalize() for d in drugs_std]) # Join drug names after capitalizing
        
        if len(drugs_std) == 0:
            pill_icon = "pill-off"
        elif len(drugs_std) == 1:
            pill_icon = "pill"
        elif len(drugs_std) > 1:
            pill_icon = "pill-multiple"
            
        raw_report_item = RawReportItem(
            text=f"{len(drugs_std)} standardized drugs found",
            secondary=l2_info,
            icon=pill_icon,
            reports=[l2_info]
        )
        self.reports_queue.put(raw_report_item)
        
        # Drug screening
        for drug in drugs_std:
            drug_warnings = checkDrug(drug, creat_num=creat_num, std=False)
            if drug_warnings:
                raw_report_item = RawReportItem(
                    text=F"{drug.capitalize()}",
                    secondary=F"Potential issue with {drug.capitalize()}",
                    icon="information",
                    reports=[drug_warnings]
                )
                self.reports_queue.put(raw_report_item)
        # Interaction reporting
        for offending_drugs, report in checkInterac(drugs_std, std=False):
            raw_report_item = RawReportItem(
                text=F"{offending_drugs}",
                secondary=F"Interaction between {offending_drugs}",
                icon="format-horizontal-align-center",
                reports=[report]
            )
            self.reports_queue.put(raw_report_item)

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
