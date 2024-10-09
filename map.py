import json
class Map:
    def __init__(self, map_name, stops):
        self.map_name = map_name
        self.stops = stops  # Dictionary of stops

    def get_stops(self):
        """Return stops dictionary."""
        return self.stops
        

    def add_stop(self, stop_name, coordinates, w, h):
        """Add a new stop to the map."""
        self.stops[stop_name] = {
            "coordinates": coordinates,
            "w": w,
            "h": h
        }

    def update_stop(self, stop_name, coordinates=None, w=None, h=None):
        """Update the information of an existing stop."""
        if stop_name in self.stops:
            if coordinates:
                self.stops[stop_name]["coordinates"] = coordinates
            if w:
                self.stops[stop_name]["w"] = w
            if h:
                self.stops[stop_name]["h"] = h
        else:
            print(f"Stop {stop_name} not found on map {self.map_name}.")
    
    def delete_stop(self, stop_name):
        """Remove a stop from the map."""
        if stop_name in self.stops:
            del self.stops[stop_name]
        else:
            print(f"Stop {stop_name} not found on map {self.map_name}.")

class MapManager:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.maps = self.load_maps_from_json()

    def load_maps_from_json(self):
        """Load maps from the JSON file and create Map objects."""
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)
        
        maps = {}
        for map_data in data:
            map_name = map_data["map_name"]
            stops = map_data["stops"]
            maps[map_name] = Map(map_name, stops)
        
        return maps

    def save_maps_to_json(self):
        """Save the current maps to the JSON file."""
        data = []
        for map_name, map_obj in self.maps.items():
            map_data = {
                "map_name": map_obj.map_name,
                "stops": map_obj.stops
            }
            data.append(map_data)
        
        with open(self.json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_map(self, map_name, stops=None):
        """Add a new map."""
        if map_name in self.maps:
            print(f"Map {map_name} already exists.")
        else:
            new_map = Map(map_name, stops if stops else {})
            self.maps[map_name] = new_map
            self.save_maps_to_json()

    def delete_map(self, map_name):
        """Delete a map."""
        if map_name in self.maps:
            del self.maps[map_name]
            self.save_maps_to_json()
        else:
            print(f"Map {map_name} not found.")

    def get_map(self, map_name):
        """Get a map object."""
        return self.maps.get(map_name, None)
