import os

import kivy
from kivy.app import App
from kivy.uix.label import Label # Imports Label element
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem

# from kivy.config import Config
# Config.set('graphics', 'width', '70')
# Config.set('graphics', 'height', '150')

from kivy.core.window import Window
Window.size = (300, 500)

import random

# Test
# Internals 
from standardization import getGenericName
import drugstandards
from check_drug import checkDrug, checkInterac



class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs) # Calls the superconstructor 
        self.cur_text = ""
    
    def checkBeers(self):
        accordion: Accordion = self.ids.accordion # Use element with "accordion" id (doesn't need to be bound) to assign ScrollView object
        scroll_view: ScrollView = self.ids.scroll_view
        text_in: str = self.text_in1.text
        delimiters = ["\n", ",", ";"]
        drugs = [text_in]
        for delim in delimiters:
            drugs = [txt.split(delim) for txt in drugs]
            drugs = sum(drugs, []) # flatten list
        print("Input texts: ", drugs)
        drugs_std = [drugstandards.standardize([d])[0] for d in drugs]
        drugs_std = [d for d in drugs_std if d] # Filter empty data types
        drugs_std = list(set(drugs_std)) # Screen out duplicates
        print("Standardized: ", drugs_std)
        
        accordion.clear_widgets() # Clear widgets before adding
        ac_item = AccordionItem(title=f"{len(drugs_std)} standardized drugs found", title_template="CustTitle")
        label = WrappedLabel(text=f"{drugs_std}", halign='left')
        ac_item.add_widget(label)
        accordion.add_widget(ac_item)
        
        # Drug screening
        for drug in drugs_std:
            drug_warning = checkDrug(drug, std=False)
            if drug_warning:
                ac_item = AccordionItem(title=f"Potential issues with {drug}", title_template="CustTitle")
                label = WrappedLabel(text=f"{drug_warning}", halign='left')
                ac_item.add_widget(label)
                accordion.height += 50 # Add room to accordion to accomodate new item
                accordion.add_widget(ac_item)
        # Interaction reporting
        for offending_drugs, report in checkInterac(drugs_std, std=False):
            ac_item = AccordionItem(title=f"Interaction between {offending_drugs}", title_template="CustTitle")
            label = WrappedLabel(text=f"{report}", halign='left')
            ac_item.add_widget(label)
            accordion.height += 50 #  Add room to accordion to accomodate new item
            accordion.add_widget(ac_item)
        
    def checkBeers1(self):
        accordian: Accordion = self.ids.accordion # Use element with "accordion" id (doesn't need to be bound) to assign ScrollView object
        for i in range(5):
            ac_item = AccordionItem(title=f"Accordian item {i}")
            ac_item.add_widget(Label(text=f"Some content of {i}"))
            accordian.add_widget(ac_item)
        print(self.ids.accordion)
        

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
