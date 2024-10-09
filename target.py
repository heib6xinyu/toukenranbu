import json
class Target:
    def __init__(self, tar_name, tar_type, scenes = None):
        """
        Initialize a Target object.

        Parameters:
        - tar_type (str): The type of target (e.g., button, map, scene, status).
        - tar_name (str): The name of the target (main identifier).
        :param scenes: A dictionary of dictionary. Each dictionary contains:
                        - Key: The name of the scene where the target appears.
                        - Value: A list of coordinates (x, y) and two additional items: width (w) and height (h).
        """
        self.tar_type = tar_type
        self.tar_name = tar_name
        self.scenes = scenes if scenes else {}

    def get_coordinates(self, scene):
        """
        Get the coordinates for a specific scene.
        
        Parameters:
        - scene (str): The scene to get coordinates for.

        Returns:
        - A dictionary: The list of coordinates for the target in the specified scene, or None if not found.
                        The w, 
                        The h
        """
        return self.scenes[scene]
    
    def get_name(self):
        return self.tar_name
    
    def get_type(self):
        return self.tar_type
    
    def add_coordinates(self, scene_name, coords, w, h):
        """
        Add or update coordinates for a specific scene.
        
        :param scene_name: The name of the scene where the target appears.
        :param coordinates: List of tuples representing coordinates (x, y).
        :param w: Width of the target.
        :param h: Height of the target.
        """
        # Check if the scene already exists
        if scene_name in self.scenes:
            # Update existing scene coordinates, width, and height
            self.scenes[scene_name]["coordinates"] = coords
            self.scenes[scene_name]["w"] = w
            self.scenes[scene_name]["h"] = h
            
                
        
        else:
            # Add new scene with coordinates, width, and height
            self.scenes[scene_name] = {
                    "coordinates": coords,
                    "w": w,
                    "h": h
                }
        


class TargetManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path

    def load_targets_from_json(self):
        """ 
        Load targets from JSON file and return a dictionary 
        where tar_name is the key and Target objects are the values.
        """
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)

        # Create a dictionary with tar_name as the key
        targets_dict = {target_data['tar_name']: Target(**target_data) for target_data in data}
        
        return targets_dict

    def save_targets_to_json(self, targets):
        """ Save a list of Target objects to JSON file. """
        data = [{'tar_type': t.tar_type, 'tar_name': t.tar_name, 'scenes': t.scenes} for t in targets]
        with open(self.json_file_path, 'w') as file:
            json.dump(data, file, indent=4)