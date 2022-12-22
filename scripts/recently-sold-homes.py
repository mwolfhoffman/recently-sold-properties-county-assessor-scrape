from bs4 import BeautifulSoup
from time import sleep
from requests_html import HTMLSession


class Property:
    def __init__(self, address: str, status_text: str) -> None:
        self.address = address
        self.date_sold = self.parse_status_text(status_text)

    def __str__(self) -> str:
        return f"address:{self.address}, date_sold: {self.date_sold}"

    def parse_status_text(self, status_text) -> str:
        prefix = "Sold - "
        if status_text == None or prefix not in status_text:
            return ""

        split = status_text.split(prefix)
        return split[1]


def scrape_realtor_for_recently_sold_homes(location, page):
    session = HTMLSession()
    url = f"https://www.realtor.com/realestateandhomes-search/{location}/show-recently-sold/pg-{page}"
    response = session.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        total_pages = soup.select_one(
            '#srp-body > section.jsx-2905457505.srp-content > div.jsx-2905457505.pagination-wrapper.text-center > div > a:nth-child(8)').text

        cards = soup.find_all("li", {"class": "component_property-card"})

        properties = []

        for card in cards:
            address = card.find('div', {"class": "address"}).text if card.find(
                'div', {"class": "address"}) else None
            status_text = card.find('span', {"class": "statusText"}).text if card.find(
                'span', {"class": "statusText"}) else ""

            if address != None:
                prop = Property(address=address, status_text=status_text)
                properties.append(prop)

        print(*properties, sep=' \n')


scrape_realtor_for_recently_sold_homes('Salt-Lake-County_UT', 1)


# TODO: work in progress. Will also need to find homeowners after recently sold.
# https://requests.readthedocs.io/projects/requests-html/en/latest/
