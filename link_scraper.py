import json
import time
import random
import nodriver as uc
import asyncio

GENRE_NUMBERS = {
    4: "Rock",
    8: "Metal",
    14: "Pop",
    666: "Folk",
    49: "Country",
    1787: "RnB",
    16: "Electronic",
}

SONG_CAP = 4000         # Max number of songs per genre
SONGS_PER_PAGE = 50     # Songs per page

async def wait_for_min_links(tab, selector, min_count=50, timeout=8000, interval=0.25):
    elapsed = 0
    while elapsed < timeout:
        try:
            elems = await tab.query_selector_all(selector)
            if len(elems) >= min_count:
                return elems
        except Exception:
            pass
        await asyncio.sleep(interval)
        elapsed += int(interval * 1000)

    if len(elems) >= min_count - 5:
        return elems
    return []

async def scrape_links(genre_num, browser):
    base_url = "https://www.ultimate-guitar.com/explore"
    all_links = []
    song_names = set()
    page = 0

    while len(all_links) < SONG_CAP and page < 100:
        page += 1
        url = f"{base_url}?order=hitstotal_desc&genres[]={genre_num}&page={page}&type[]=Chords"
        tab = await browser.get(url)

        await asyncio.sleep(random.uniform(1.5, 2.5))  # Small delay to avoid being blocked

        link_elems = await wait_for_min_links(tab, "a[tabcount]")

        links = []
        for elem in link_elems:
            num_names = len(song_names)
            if elem.text.find("(") != -1:
                song_names.add(elem.text[:elem.text.find(" (")])
            else:
                song_names.add(elem.text)
            if len(song_names) == num_names:
                continue
            links.append(elem.attributes[5])

        all_links.extend(links)

        print(f"Page {page}: Found {len(links)} links; Sample link: {links[0]}")

        # Add delay between pages to avoid IP bans
        await asyncio.sleep(random.uniform(0, 1))

    genre_name = GENRE_NUMBERS[genre_num].lower().replace('-', '')
    filename = f"scraped_data/{genre_name}_links.json"
    with open(filename, "w") as f:
        json.dump(all_links, f, indent=2)

    print(f"✅ Scraped {len(all_links)} links for genre: {GENRE_NUMBERS[genre_num]}")
    

async def main():
    browser = await uc.start(
                headless=True,
                browser_args=['--no-sandbox', '--disable-dev-shm-usage', 
                              '--disable-blink-features=AutomationControlled', 
                              '--ignore-certificate-errors', '--ignore-ssl-errors',
                              '--headless=new',
                              '--start-maximized'],
                lang="en-US"   # this could set iso-language-code in navigator, not recommended to change
            )
    
    for genre_num in GENRE_NUMBERS.keys():
        print(f"Scraping links for genre: {GENRE_NUMBERS[genre_num]}")
        await scrape_links(genre_num, browser)
        print(f"Finished scraping links for genre: {GENRE_NUMBERS[genre_num]}")

    browser.stop()
    
if __name__ == "__main__":
    uc.loop().run_until_complete(main())
