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

def get_song_dataset_stats():
    """
    Get the number of songs in the 'all_chords' directory; calculate the average number of chords per song as well
    as range statistics (most chords in a song, least chords in a song). In addition, collect all unique chords
    and return the list of unique chords.
    """
    try:
        print(f"Dataset Statistics")
        with open('all_chords/all_chords.json', 'r') as f:
            data = json.load(f)
            print(f"Total number of songs: {len(data)}")

            chord_counts = [len(details['chord_list']) for details in data.values() if 'chord_list' in details]
            avg_chords = sum(chord_counts) / len(chord_counts)
            most_chords = max(chord_counts)
            least_chords = min(chord_counts)
            print(f"Average number of chords per song: {avg_chords}")
            print(f"Most chords in a song: {most_chords}")
            print(f"Least chords in a song: {least_chords}")

            unique_chords = set()
            for details in data.values():
                unique_chords.update(details.get('chord_set', []))

            print(f"Total unique chords: {len(unique_chords)}")
            print(f"Unique chords: {sorted(unique_chords)}")
            
    except FileNotFoundError:
        print("❌ Error: 'all_chords/all_chords.json' file not found.")


if __name__ == "__main__":
    # create_set_from_all_json_files()
    # combine_all_chords()
    # get_unscraped_links()
    get_song_dataset_stats()