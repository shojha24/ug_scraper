import json
import time
import random
import asyncio
from pathlib import Path
from tqdm import tqdm
import nodriver as uc
import re
import bs4

# Regex to extract individual chords from a line
chord_token = re.compile(
    r"([A-G](?:#|b)?(?:maj|min|dim|aug|sus|add|m|\+)?\d*(?:\/[A-G](?:#|b)?)?)"
)

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

async def wait_for_html(tab, selector: str, timeout=6, interval=0.2):
    """
    Repeatedly tries to find the selector until timeout is reached.
    Returns the parsed HTML or None if not found.
    """
    curr_val = None
    max_attempts = int(timeout / interval)
    for _ in range(max_attempts):
        node = await tab.query_selector(selector)
        if node:
            # Check if the node has fully loaded, i.e. it hasn't changed since the last check
            new_html = await node.get_html()
            new_val = bs4.BeautifulSoup(new_html, 'html.parser')
            if new_val == curr_val:
                return curr_val
            curr_val = new_val
        await asyncio.sleep(interval)
    return curr_val

# --- Your extraction logic (unchanged, it's good) ---

async def extract_chords_by_section(container):
    try:
        # Wait for the <pre> element (which holds the chord tab)
        soup = await wait_for_html(container, "pre")
        if not soup:
            return {"count": 0, "chord_list": [], "chord_set": []}
        
        # Get all <span> elements with attribute data-name set to something
        spans = soup.find_all("span", attrs={"data-original-chord": True})

        # Extract the text from these spans
        all_chords_list = [span.get_text(strip=True) for span in spans if span.get_text(strip=True)]

        if not all_chords_list:
            return {"count": 0, "chord_list": [], "chord_set": []}

        # Initial state

        song_info = {}
        all_chords_set = set()

        all_chords_set.update(all_chords_list)
        song_info["chord_set"] = list(all_chords_set)
        song_info["chord_list"] = all_chords_list
        song_info["count"] = len(all_chords_list)

        return song_info

    except Exception:
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

            # 1. Open each link in a new, fresh tab
            tab = await browser.get(link, new_tab=True)

            await asyncio.sleep(random.uniform(1.7, 2))  # Give the tab some time to load

            # Validate the chart content
            is_valid = await is_valid_chart(tab)
            if not is_valid:
                tqdm.write(f"⚠️ Invalid or inaccessible chart: {link}")
                continue

            # Extract data
            song_info = await extract_chords_by_section(tab)

            # Store valid results
            if song_info and song_info.get("count", 0) > 0:
                results[link] = song_info
                tqdm.write(f"✅ Scraped {song_info['count']} chords from {link}")
            else:
                tqdm.write(f"❌ No valid chords found in {link}")

            try:
                await tab.close()
            except Exception as close_e:
                tqdm.write(f"⚠️ Could not close tab for {link}: {close_e}")
            
            # A small delay can help avoid rate-limiting
            await asyncio.sleep(random.uniform(0.0, 0.4))

        except Exception as e:
            tqdm.write(f"❌ Error scraping {link}: {e}")
        
    return results


# --- Main execution block (unchanged, it's good) ---

async def main():
    if not links:
        return

    browser = await uc.start(
        headless=True, # Set to True for production runs
        browser_args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--headless=new",  # ✅ Use new headless mode (headful-like behavior)
            "--window-size=129,826",
            "--start-maximized",
            "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        ],
        lang="en-US"
    )

    tqdm.write("🛠️ Browser initialized...")

    batch_size = 5 # Number of links to scrape in one go
    links_done = 0
    total_links = 5

    while links_done < total_links:
        first_tab = links_done
        last_tab = min(links_done + batch_size, total_links)
        tqdm.write(f"Scraping links from {first_tab} to {last_tab}...")

        parsed_data = await scrape_tabs(browser, first_tab, last_tab)

        # Save the scraped data
        Path("all_chords").mkdir(exist_ok=True)
        with open(f"all_chords/chord_sections_{first_tab}_{last_tab}.json", "w") as f:
            json.dump(parsed_data, f, indent=2)

        links_done = last_tab

        browser.stop()

        browser = await uc.start(
            headless=True, # Set to True for production runs
            browser_args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--headless=new",  # ✅ Use new headless mode (headful-like behavior)
                "--window-size=129,826",
                "--start-maximized",
                "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            ],
        )
    
    print("🛑 Stopping browser.")
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
