import json
import os

def create_set_from_all_json_files():
    """
    Create a set containing all unique items from all JSON files in the specified directory.
    """
    unique_items = set()
    
    for filename in os.listdir('scraped_data'):
        if filename.endswith('.json') and filename != 'unique_links.json':
            with open(f'scraped_data/{filename}', 'r') as file:
                data = json.load(file)
                unique_items.update(data)

    with open('scraped_data/unique_links.json', 'w') as outfile:
        json.dump(list(unique_items), outfile, indent=2)

def combine_all_chords():
    """
    Combine all unique chords from the JSON files in the 'all_chords' directory into a single set.
    """
    all_chords = {}

    for filename in os.listdir('all_chords'):
        if filename.endswith('.json'):
            with open(f'all_chords/{filename}', 'r') as file:
                data = json.load(file)
                for chord, details in data.items():
                    if chord not in all_chords:
                        all_chords[chord] = details
                    else:
                        # If the chord already exists, merge the details
                        all_chords[chord].update(details)

    with open('all_chords/all_chords.json', 'w') as outfile:
        json.dump(all_chords, outfile, indent=2)



if __name__ == "__main__":
    # create_set_from_all_json_files()
    combine_all_chords()



