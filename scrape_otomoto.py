from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import time
import shelve
import os
import shutil
from moto import *

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
    print(e)

def log_verbose(string, verbose_switch, end="\n"):
    if verbose_switch:
        print(string, end=end)

def scrape_offer_list(dist = 50, loc = 'lodz', cat = 'motocykle-i-quady', verbose_switch = False):
    base_url = 'https://www.otomoto.pl'
    post_url = f'?search[order]=created_at_first%3Adesc&search[dist]={dist}&search[country]='
    url = '/'.join([base_url, cat, loc, post_url])

    raw_html = simple_get(url)
    soup = BeautifulSoup(raw_html, 'html.parser')

    page_buttons = soup.find_all(class_="page")
    if len(page_buttons) > 1:
        num_pages = int(page_buttons[-1].contents[0])
    else:
        num_pages = 1
    log_verbose(f'Otomoto pages found: {num_pages}', verbose_switch)

    soup_list = [soup]
    for page_idx in range(2, num_pages):
        url += f'&page={page_idx}'
        raw_html = simple_get(url)
        soup_list.append(BeautifulSoup(raw_html, 'html.parser'))
        log_verbose(f'download {((page_idx / num_pages) * 100):.0f}%', verbose_switch, end="\r")
        
    timestamp = time.strftime("%Y_%m_%d", time.localtime())
    db_directory = f"snapshot_{timestamp}"
    if os.path.isdir(db_directory):
        shutil.rmtree(db_directory)
    os.mkdir(db_directory)
    offer_file = open(f"{db_directory}/offer_file.html", "w+")
    moto_shelf_filename = f"{db_directory}/moto_shelf"
    moto_shelf = shelve.open(moto_shelf_filename)

    for soup_counter, soup in enumerate(soup_list):
        log_verbose(f'interpreting {((soup_counter / num_pages) * 100):.0f}%', verbose_switch, end="\r")
        for offer in soup.find_all(class_="offer-item__content ds-details-container"):
            offer_file.write(str(offer))

            offer_model = offer.find(class_="offer-title__link").attrs['title']

            offer_link = offer.find(class_="offer-title__link").attrs['href']

            offer_id = int(offer.find(class_="offer-title__link").attrs['data-ad-id'])

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

            moto = motorcycle_offer(model_name = offer_model, capacity_cm3 = offer_capacity, price = offer_price, currency = offer_currency, url = offer_link, body = offer_body, mileage = offer_mileage, year = offer_year)
            moto_shelf[str(offer_id)] = moto

    moto_shelf.close()

    log_verbose(f'Dumped to {db_directory}/', verbose_switch)

    return moto_shelf_filename

if __name__ == "__main__":
    scrape_offer_list(verbose_switch=True)
