import kivy
from kivy.app import App
from kivy.uix.label import Label # Imports Label element
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.widget import Widget
import random

class RootLayout(BoxLayout): # Constructs a UI element based on the kivy BoxLayout class 
    def __init__(self):
        super(RootLayout, self).__init__() # Calls the superconstructor 

    def genNumber(self):
        self.display_label.text = str(random.randint(0, 100)) # Label call refers to identifier within .kv file

class MainWidget(Widget): # Widget within app 
    pass



class BeersApp(App): 
    """
    This class inherits the App class from kivy
    The name of this class will also determine the name of the .kv files (for layout/design)
    .kv file name is not case-sensitive to the class name but should be all lowercase to avoid issues
    """
    
    def build(self): # Returns the UI
        return RootLayout() # Return whatever element you are using for the UI


app_instance = BeersApp() # Creates instance of the app
app_instance.run() # Runs the instance of the app 
