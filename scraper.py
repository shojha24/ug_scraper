from bs4 import BeautifulSoup
import requests
import json

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def get_chords(soup):
    chord_div = soup.find("div", {"class": "js-store"})
    data_content = chord_div['data-content']
    chords_loaded_json = json.loads(data_content)
    return chords_loaded_json["store"]["page"]["data"]["tab_view"]["wiki_tab"]["content"].replace("[tab]", "").replace("[/tab]", "").replace("[ch]", "").replace("[/ch]","")

# dw abt this functionality this is just so that i can test the code w/o changing it all the time

input_url = input("Enter the url: ")

print(get_chords(get_soup(input_url)))