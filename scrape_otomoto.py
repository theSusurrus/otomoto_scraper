import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import time
import shelve
import os
import shutil
from moto import *

class progress_description:
    def __init__(self, progress=0, description=''):
        self.progress = progress
        self.description = description

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(requests.get(url, stream=True)) as resp:
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

def scrape_offer_list(dist, loc, shelf_name=None, shelf_ready_event=None, progress_queue=None, scrape_details=False, cat = 'motocykle-i-quady', verbose_switch = False):
    if shelf_ready_event is not None:
        shelf_ready_event.clear()

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

        progress = (page_idx / num_pages)
        log_message = f'Downloading {progress * 100:.0f}%'
        if progress_queue is not None:
            progress_queue.put(progress_description(progress, log_message))
        log_verbose(log_message, verbose_switch, end="\r")

    if shelf_name is None:
        timestamp = time.strftime("%Y_%m_%d", time.localtime())
        if not os.path.isdir('data/'):
            os.mkdir('data/')
        db_directory = f"data/snapshot_{loc}_{dist}_{timestamp}"
        if os.path.isdir(db_directory):
            shutil.rmtree(db_directory)
        os.mkdir(db_directory)
        shelf_name = f"{db_directory}/moto_shelf"
    moto_shelf = shelve.open(shelf_name)

    for soup_counter, soup in enumerate(soup_list):
        progress = soup_counter / num_pages
        log_message = f'Interpreting {(progress * 100):.0f}%'
        log_verbose(log_message, verbose_switch, end="\r")
        if progress_queue is not None:
            progress_queue.put(progress_description(progress, log_message))
        for offer in soup.find_all(class_="offer-item__content ds-details-container"):
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
                offer_price = None
            
            offer_currency_tag = offer.find(class_="offer-price__number ds-price-number")
            if offer_currency_tag is not None:
                offer_currency = offer_currency_tag.find("span", {"data-type" : "price_currency_2"}).contents[0]
            else:
                offer_currency = None

            moto = motorcycle_offer(model_name = offer_model, capacity_cm3 = offer_capacity, price = offer_price, currency = offer_currency, url = offer_link, body = offer_body, mileage = offer_mileage, year = offer_year, moto_id=offer_id)
            moto_shelf[str(offer_id)] = moto

    if scrape_details:
        num_offers = len(moto_shelf)
        for index, (key, moto) in enumerate(moto_shelf.items()):
            progress = soup_counter / num_pages
            log_message = f'Downloading photos {int((index / num_offers) * 100)}%'
            log_verbose(log_message, verbose_switch, end="\r")
            if progress_queue is not None:
                progress_queue.put(progress_description(progress, log_message))
            moto_shelf[key] = scrape_details_for_offer(moto, verbose_switch=False)

    moto_shelf.close()

    log_verbose(f'Dumped snapshot to {shelf_name}', verbose_switch)

    if shelf_ready_event is not None:
        shelf_ready_event.set()

    return shelf_name

def scrape_details_for_offer(moto, verbose_switch=False):
    if not os.path.isdir("data"):
        os.mkdir("data")
    offer_dir = f'data/{moto.moto_id}'
    if not os.path.isdir(offer_dir):
        os.mkdir(offer_dir)
        raw_html = simple_get(moto.url)
        soup = BeautifulSoup(raw_html, 'html.parser')
        photo_tags = soup.find_all(class_="bigImage")
        for photo_idx, photo_tag in enumerate(photo_tags):
            log_verbose(f'Downloading photos for offer {int(photo_idx / len(photo_tags) * 100)}%', verbose_switch, end='\r')
            photo_url = photo_tag.attrs['data-lazy']
            with open(f'{offer_dir}/img{photo_idx}.jpg', 'wb') as photo_file:
                response = requests.get(photo_url, stream=True)
                if not response.ok:
                    print(response)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    photo_file.write(block)
        description_tag = soup.find(class_="offer-description__description")
        description_text = [str(content).replace('\n', '').strip() for content in description_tag.contents if isinstance(content, str) and str(content) != '\n']
        moto.description = '\n'.join(description_text)
    return moto

if __name__ == "__main__":
    scrape_offer_list(loc='lodz', dist=5, verbose_switch=True, scrape_details=True)
