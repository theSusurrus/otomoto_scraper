from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import time

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just result.appends them, but you can
    make it do anything.
    """
    result.append(e)


class motorcycle_offer:
    def __init__(self, model_name, capacity_cm3, price_PLN, url, body, mileage):
        self.model_name = model_name
        self.capacity_cm3 = capacity_cm3
        self.price_PLN = price_PLN
        self.url = url
        self.body = body
        self.mileage = mileage

    def __str__(self):
        result = []
        header_width = 40
        filler = int((header_width - len(self.model_name)) / 2)
        header_string = '-' * filler + self.model_name + '-' * filler + '\n'
        result.append(header_string)
        result.append(f'{self.capacity_cm3} capacity\n')
        result.append(f'{self.mileage}\n')
        result.append(f'{self.price_PLN}\n')
        result.append(f'{self.url}\n')
        result.append('\n')
        return ''.join(result)

base_url = 'https://www.otomoto.pl/'
loc_url = 'lodz/'
cat_url = 'motocykle-i-quady/'
post_url = '?search[order]=created_at_first%3Adesc&search[dist]=100&search[country]='
url = base_url + cat_url + loc_url + post_url

raw_html = simple_get(url)
soup = BeautifulSoup(raw_html, 'html.parser')

page_buttons = soup.find_all(class_="page")
num_pages = int(page_buttons[-1].contents[0])
print(f'otomoto pages found: {num_pages}')

soup_list = [soup]
for page_idx in range(2, num_pages):
    url += f'&page={page_idx}'
    raw_html = simple_get(url)
    soup_list.append(BeautifulSoup(raw_html, 'html.parser'))

timestamp = time.strftime("%Y_%m_%d", time.localtime())

moto_list = []
offer_file = open(f"offer_file_{timestamp}.html", "w+")
moto_file = open(f"offer_file_{timestamp}.csv", "w+")
pretty_file = open(f"pretty_otomoto_{timestamp}.html", "w+")
for soup in soup_list:
    pretty = soup.prettify()
    pretty_file.write(pretty)
    for offer in soup.find_all(class_="offer-item__content ds-details-container"):
        offer_file.write(str(offer))

        offer_model = offer.find(class_="offer-title__link").attrs['title']

        offer_link = offer.find(class_="offer-title__link").attrs['href']

        offer_year_tag = offer.find("li", {"data-code" : "year"})
        if offer_year_tag is not None:
            offer_year = offer_year_tag.find("span").contents[0]
        else:
            offer_year = None

        offer_mileage_tag = offer.find("li", {"data-code" : "mileage"})
        if offer_mileage_tag is not None:
            offer_mileage = offer_mileage_tag.find("span").contents[0]
            offer_mileage = offer_mileage.replace(' ', '')
            offer_mileage = offer_mileage.replace('km', '')
            offer_mileage = int(offer_mileage)
        else:
            offer_mileage = None

        offer_capacity_tag = offer.find("li", {"data-code" : "engine_capacity"})
        if offer_capacity_tag is not None:
            offer_capacity = offer_capacity_tag.find("span").contents[0]
            offer_capacity = offer_capacity.replace(' ', '')
            offer_capacity = offer_capacity.replace('cm3', '')
            offer_capacity = int(offer_capacity)
        else:
            offer_capacity = None

        offer_body_tag = offer.find("li", {"data-code" : "body_type"})
        if offer_body_tag is not None:
            offer_body = offer_body_tag.find("span").contents[0]
        else:
            offer_body = None

        offer_price_tag  = offer.find(class_="offer-price__number ds-price-number")
        if offer_price_tag is not None:
            offer_price = offer_price_tag.contents[1].contents[0]
            offer_price = offer_price.replace(' ', '')
            offer_price = int(offer_price)
        else:
            None
        
        offer_currency_tag = offer.find(class_="offer-price__number ds-price-number")
        if offer_currency_tag is not None:
            offer_currency = offer_currency_tag.find("span", {"data-type" : "price_currency_2"}).contents[0]
        else:
            offer_currency = None

        moto_file.write(f'{offer_model},{offer_year},{offer_mileage},{offer_capacity},{offer_body},{offer_price},{offer_currency},{offer_link}\n')

        moto_list.append(motorcycle_offer(model_name = offer_model, capacity_cm3 = offer_capacity, price_PLN = offer_price, url = offer_link, body = offer_body, mileage = offer_mileage))

# pretty_list_file = open(f"pretty_list{timestamp}.txt", "w+")
# for m in moto_list:
#     pretty_list_file.write(str(m))
