import os

import kivy
from kivy.app import App
from kivy.uix.label import Label # Imports Label element
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
import random

# Test
# Internals 
from standardization import getGenericName
from check_drug import checkDrug



class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs) # Calls the superconstructor 
        self.cur_text = ""

    def getGeneric(self):
        text_in: str = self.text_in1.text
        print(text_in)
        generic = getGenericName(text_in)
        self.display_label.text = generic
        pass
    
    def checkBeers(self):
        text_in: str = self.text_in1.text
        if "\n" in text_in:
            print("Newline character detected")
        texts = text_in.split("\n")     
        print("Input texts: ", texts)
        report = ""
        for text in texts:
            report += checkDrug(text) + "\n---------------------\n"
        self.display_label.text = report







class BeersApp(App): 
    """
    This class inherits the App class from kivy
    The name of this class will also determine the name of the .kv files (for layout/design)
    .kv file name is not case-sensitive to the class name but should be all lowercase to avoid issues
    .kv file name can exclude "App" portion of App class identifier
    """
    
    def build(self): # Returns the UI
        return RootLayout() # Return whatever root element you are using for the UI
        


app_instance = BeersApp() # Creates instance of the app
app_instance.run() # Runs the instance of the app 
