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

def get_unscraped_links():
    """
    Get a list of links that have not been scraped yet.
    """
    try:
        scraped_links = set()
        all_links = set()

        with open('all_chords/all_chords.json', 'r') as f:
            scraped_links = set(json.load(f).keys())
        with open('scraped_data/unique_links.json', 'r') as f:
            all_links = set(json.load(f))

        links = list(all_links - scraped_links)

        with open('scraped_data/unscraped_links.json', 'w') as f:
            json.dump(links, f, indent=2)
        
    except FileNotFoundError:
        print("❌ Error: file not found. Please create the file with a list of URLs.")

def get_song_num():
    """
    Get the number of songs in the 'all_chords' directory.
    """
    try:
        with open('all_chords/all_chords.json', 'r') as f:
            data = json.load(f)
            return len(data)
    except FileNotFoundError:
        print("❌ Error: 'all_chords/all_chords.json' file not found.")
        return 0


if __name__ == "__main__":
    # create_set_from_all_json_files()
    # combine_all_chords()
    # get_unscraped_links()
    print(f"Total number of songs: {get_song_num()}")