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
    45: "Hip-Hop",
    16: "Electronic",
    216: "Classical",
    84: "Jazz",
    1016: "Worship",
    680: "Soundtrack",
    1781: "Reggae"
}

SONG_CAP = 5000         # Max number of songs per genre
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

    try:
        for page in range(1, (SONG_CAP // SONGS_PER_PAGE) + 1):
            url = f"{base_url}?order=hitstotal_desc&genres[]={genre_num}&page={page}"
            tab = await browser.get(url)
            link_elems = await wait_for_min_links(tab, "a[tabcount]")
            links = [elem.attributes[5] for elem in link_elems]
            all_links.extend(links)

            print(f"Page {page}: Found {len(link_elems)} links; Sample link: {links[0]}")

            # Add delay between pages to avoid IP bans
            time.sleep(random.uniform(0, 2))

    finally:
        pass

    genre_name = GENRE_NUMBERS[genre_num].lower().replace('-', '')
    filename = f"{genre_name}_links.json"
    with open(filename, "w") as f:
        json.dump(all_links, f, indent=2)

    print(f"✅ Scraped {len(all_links)} links for genre: {GENRE_NUMBERS[genre_num]}")
    

async def main():
    browser = await uc.start(
                headless=False,
                browser_args=['--no-sandbox', '--disable-dev-shm-usage', 
                              '--disable-blink-features=AutomationControlled', 
                              '--ignore-certificate-errors', '--ignore-ssl-errors',
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
