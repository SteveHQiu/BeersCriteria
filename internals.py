from dataclasses import dataclass
from enum import Enum

# Dataclasses

class NodeType(Enum):
    ICON = 1
    LABEL = 2


@dataclass
class RawReportItem:
    """
    Container for strings to be loaded into widgets
    Bridge between calculation thread and rendering main thread
    """
    
    text: str
    secondary: str = ""
    icon: str = "minus-circle"
    children: list = None # List of RawReportItem, can't define recursively in dataclass
    node_type: int = NodeType.ICON