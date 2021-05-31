"""
Build main components for harbour management and
ships movements registry.

Classes:
    Harbour
    Pier
    Berth
    Ship
    Movements
"""

class Berth:
    """
    """
    def __init__(self, length, equipements={}, is_empty=None):
        self.length = length
        self.equipements = equipements
        self.is_empty = is_empty



class Harbour:
    """
    Class defining the harbour

    Can have 0 or multiple initial piers.

    Args:
        piers: list of pier objects
    """
    def __init__(self, piers=[]):
        self.piers = piers 



class Movements:
    """
    """
    def __init__(self):
        self.movements = []



class Pier:
    """
    Pier object 
    """
    def __init__(self, berths=[]):
        self.berths = berths



class Ship:
    """
    """
    def __init__(self, name, id, ship_type, length):
        self.name = name
        self.id = id
        self.ship_type = ship_type
        self.length = length
