from enum import Enum

from .advertisement import Advertisement

class ChangeType(Enum):
    new = 0
    updated = 1
    deleted = 2
    none = 3

class AdvertisementChange(dict):
    
    def __init__(self, ad: Advertisement, change_type: ChangeType, change: str):
        dict.__init__(self, ad = ad, change_type = change_type, change = change)
        self.ad = ad
        self.change_type = change_type
        self.change = change
        pass
    pass