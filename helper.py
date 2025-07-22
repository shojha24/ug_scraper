import json
import os

def create_set_from_all_json_files():
    """
    Create a set containing all unique items from all JSON files in the specified directory.
    """
    unique_items = set()
    
    for filename in os.listdir('.'):
        if filename.endswith('.json') and filename != 'unique_links.json':
            with open(filename, 'r') as file:
                data = json.load(file)
                unique_items.update(data)

    with open('unique_links.json', 'w') as outfile:
        json.dump(list(unique_items), outfile, indent=2)

create_set_from_all_json_files()
