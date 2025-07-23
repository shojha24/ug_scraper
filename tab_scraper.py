import json
import time
import random
import asyncio
from pathlib import Path
from tqdm import tqdm
import nodriver as uc

# It's a good practice to load this once at the top
try:
    with open('scraped_data/unique_links.json', 'r') as f:
        links = json.load(f)
except FileNotFoundError:
    print("❌ Error: 'scraped_data/unique_links.json' not found. Please create the file with a list of URLs.")
    links = []


# Check if chord chart is still valid

async def is_valid_chart(container):
    invalid_elem = await container.query_selector("a[href='https://www.ultimate-guitar.com/article/blog/licensing']")
    return invalid_elem is None

# Polling to make sure we can scrape the link properly

async def wait_for_selector(tab, selector: str, timeout=10_000, interval=0.5):
    """
    Repeatedly tries to find the selector until timeout is reached.
    Returns the NodeHandle or None if not found.
    """
    max_attempts = int(timeout / (interval * 1000))
    for _ in range(max_attempts):
        node = await tab.query_selector(selector)
        if node:
            return node
        await asyncio.sleep(interval)
    return None

# --- Your extraction logic (unchanged, it's good) ---

async def extract_chords_by_section(container):
    try:
        try: 
            pre_element = await wait_for_selector(container, "pre")
        except:
            return {"sections": {}, "count": 0}
        if not pre_element:
            return {"sections": {}, "count": 0}

        # Get the full text content of the pre element
        pre_text = await pre_element.get_html()

        # Get all chord elements from the pre element

        chord_elements = await pre_element.query_selector_all("span[data-name]")
        if not chord_elements:
            return {"sections": {}, "count": 0}
        
        # Split the text into lines and process line by line
        lines = pre_text.split('\n')
        current_section = "Unnamed Section"
        song_info = {"sections": {current_section: []}}
        chord_count = 0
        chord_index = 0  # Track which chord element we're processing

        for line in lines:
            line = line.strip()
            
            # Check if this line is a section header
            if line.startswith("[") and line.endswith("]"):
                current_section = line.strip("[]").strip()
                if not current_section:
                    current_section = "Blank Section"
                song_info["sections"].setdefault(current_section, [])
                continue
            
            # Count how many chord spans should be in this line
            # We'll extract chords in order as they appear
            line_chord_count = line.count('data-name="')
            
            # Extract the corresponding number of chords from our chord_elements list
            for _ in range(line_chord_count):
                if chord_index < len(chord_elements):
                    try:
                        chord_elem = chord_elements[chord_index]
                        chord_name = chord_elem.attributes[1]
                        if chord_name and chord_name.strip():
                            song_info["sections"][current_section].append(chord_name.strip())
                            chord_count += 1
                        chord_index += 1
                    except Exception as chord_e:
                        print(f"⚠️ Error extracting chord at index {chord_index}: {chord_e}")
                        chord_index += 1
                        continue

        # Clean up empty sections
        song_info["sections"] = {k: v for k, v in song_info["sections"].items() if v}
        song_info["count"] = chord_count

        return song_info

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {}

# --- THE MAIN FIX IS HERE ---

async def scrape_tabs(browser, first_tab=None, last_tab=None):
    results = {}
    links_to_scrape = links[first_tab:last_tab] if (first_tab is not None and last_tab is not None) else links
    if not links_to_scrape:
        return {}

    # Use tqdm on the list of links
    for link in tqdm(links_to_scrape, desc="Scraping Tabs"):
        tab = None  # Define tab here to ensure it's available in the finally block
        try:

            # Skip non-chord pages
            if "chords" not in link:
                tqdm.write(f"⏩ Skipping non-chord link: {link}")
                continue

            # 1. Open each link in a new, fresh tab
            tab = await browser.get(link, new_tab=True)

            await asyncio.sleep(random.uniform(1, 2))

            # Validate the chart content
            is_valid = await is_valid_chart(tab)
            if not is_valid:
                tqdm.write(f"⚠️ Invalid or inaccessible chart: {link}")
                continue

            # Extract data
            song_info = await extract_chords_by_section(tab)

            # Store valid results
            if song_info and song_info.get("count", 0) > 8:
                results[link] = song_info
                tqdm.write(f"✅ Scraped {song_info['count']} chords from {link}")
            
            # A small delay can help avoid rate-limiting
            await asyncio.sleep(random.uniform(0, 1))

        except Exception as e:
            tqdm.write(f"❌ Error scraping {link}: {e}")
        
        finally:
            # 2. Always close the tab to free up resources
            if tab:
                try:
                    await tab.close()
                except Exception as close_e:
                    tqdm.write(f"⚠️ Could not close tab for {link}: {close_e}")
    return results


# --- Main execution block (unchanged, it's good) ---

async def main():
    if not links:
        return

    browser = await uc.start(
        headless=False, # Set to True for production runs
        browser_args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled'
        ],
        lang="en-US"
    )

    try:
        first_tab = 0
        last_tab = 10  # Set a limit for testing, adjust as needed
        parsed_data = await scrape_tabs(browser, first_tab, last_tab)

        Path("scraped_data").mkdir(exist_ok=True)
        with open(f"scraped_data/chord_sections_{first_tab}_{last_tab}.json", "w") as f:
            json.dump(parsed_data, f, indent=2)
            
        print(f"\n✅ Finished! Scraped {len(parsed_data)} songs with >8 chords.")
    finally:
        print("🛑 Stopping browser.")
        browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
