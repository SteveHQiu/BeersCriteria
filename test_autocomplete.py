# From https://www.reddit.com/r/kivy/comments/m4rw26/easiest_way_to_add_autocomplete_feature_in/
import json
from difflib import SequenceMatcher

from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
import numpy as np

with open("data/drugdict.json", "r") as file:
    DICT: dict = json.load(file)

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
        print(cscrollviews)
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
        self.text = btn.text 
        # Funcction of each buttons ends here 
        
        self.suggestions = []
        for cscrollview in cscrollviews:
            parent_layout.remove_widget(cscrollview)

KV = '''
<CButton>:
    size: self.texture_size
    padding: dp(10), dp(10)
<CScrollView>:
    id: cscrollview
    size_hint_y: 0.1
    BoxLayout:
        id: button_box
        orientation: 'horizontal'
        size_hint_x: None
        width: self.minimum_width
BoxLayout:
    orientation: 'vertical'
    AutoCompleter:
        size_hint_y: 0.1
    Button: # To up rest of space
        text: "Test"
'''

runTouchApp(Builder.load_string(KV))