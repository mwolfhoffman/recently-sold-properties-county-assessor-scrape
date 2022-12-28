from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
from typing import List
import json
import asyncio


class Property:
    def __init__(self, address: str, status_text: str) -> None:
        self.address = address.strip()
        self.date_sold = self.parse_status_text(status_text).strip()

    def __str__(self) -> str:
        return f"address:{self.address}, date_sold: {self.date_sold}"

    def parse_status_text(self, status_text) -> str:
        prefix = "Sold - "
        if status_text == None or prefix not in status_text:
            return ""

        split = status_text.split(prefix)
        return split[1]

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


properties: List[Property] = []


async def get_pages(location) -> int:
    session = AsyncHTMLSession()
    url = f"https://www.realtor.com/realestateandhomes-search/{location}/show-recently-sold/pg-1"
    response = await session.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        total_pages = soup.select_one(
            '#srp-body > section.jsx-2905457505.srp-content > div.jsx-2905457505.pagination-wrapper.text-center > div > a:nth-child(8)').text

        return int(total_pages)


async def scrape_realtor_for_recently_sold_homes(location, page):
    session = AsyncHTMLSession()
    url = f"https://www.realtor.com/realestateandhomes-search/{location}/show-recently-sold/pg-{page}"
    response = await session.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        cards = soup.find_all("li", {"class": "component_property-card"})

        for card in cards:
            address = card.find('div', {"class": "address"}).text if card.find(
                'div', {"class": "address"}) else None
            status_text = card.find('span', {"class": "statusText"}).text if card.find(
                'span', {"class": "statusText"}) else ""

            if address != None:

                prop = Property(address=address, status_text=status_text)

                properties.append(prop.to_json())


async def main(location, total_pages) -> None:

    current_page = 1
    while current_page < total_pages:
        await scrape_realtor_for_recently_sold_homes(location, 1)
        current_page += 1

    with open("./data/recently-sold.json", "w") as outfile:
        json.dump(properties, outfile)


total_pages = 0
location = "Salt-Lake-Count_UT"
loop = asyncio.get_event_loop()
tasks = [get_pages(location)]
total_pages = loop.run_until_complete(asyncio.gather(*tasks))[0]
print(total_pages)
tasks = [main(location, total_pages)]
total_pages = loop.run_until_complete(asyncio.gather(*tasks))
loop.close()
