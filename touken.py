import json
class Touken:
    def __init__(self, name, touken_type, ji):
        self.name = name
        self.touken_type = touken_type
        self.ji = ji
    
    def get_name(self):
        return self.name
    
    def get_touken_type(self):
        return self.touken_type
    
    def get_ji(self):
        return self.ji
    
    # def get_pic_path(self):
    #     return self.pic_path
    
class ToukenManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path

    def load_toukens_from_json(self):
        """ 
        Load toukens from JSON file and return a dictionary 
        where name is the key and Touken objects are the values.
        """
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)

        # Create a dictionary with tar_name as the key
        toukens_dict = {touken_data['name']: Touken(**touken_data) for touken_data in data}
        
        return toukens_dict

    def save_toukens_to_json(self, toukens):
        """ Save a list of Touken objects to JSON file. """
        data = [{'name': t.name, 'touken_type': t.touken_type, 'ji': t.ji} for t in toukens]
        with open(self.json_file_path, 'w') as file:
            json.dump(data, file, indent=4)