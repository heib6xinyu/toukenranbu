import json
class Touken:
    def __init__(self, name, touken_type, ji, pic_path):
        self.name = name
        self.touken_type = touken_type
        self.ji = ji
    
    def get_name(self):
        return self.name
    
    def get_touken_type(self):
        return self.touken_type
    
    def get_ji(self):
        return self.ji
    
    def get_pic_path(self):
        return self.pic_path
    
