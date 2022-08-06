import kivy
from kivy.app import App
from kivy.uix.label import Label # Imports Label element
from kivy.uix.boxlayout import BoxLayout # Imports layout call function which pulls from .kv file with the same name as the class that calls it
from kivy.uix.widget import Widget

class MainWidget(Widget): # Widget within app
    pass

class BeersApp(App): 
    """
    This class inherits the App class from kivy
    The name of this class will also determine the name of the .kv files (for layout/design)
    .kv file name is not case-sensitive to the class name but should be all lowercase to avoid issues
    .kv file name can exclude "App" portion of App class identifier
    """
    # Note that this version uses the beers_widget.kv version of .kv file
    # Hook for widget is in .kv file itself, don't need to do anything here
    



app_instance = BeersApp() # Creates instance of the app
app_instance.run() # Runs the instance of the app 