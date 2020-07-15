from moto import motorcycle_offer
import shelve
from color_codes import colors

def show_new_offers(old, new):
    old_shelf = shelve.open(old)
    new_shelf = shelve.open(new)
    if new_shelf and old_shelf is not None:
        old_id_list = old_shelf.keys()
        new_id_list = new_shelf.keys()
        for new_id in new_id_list:
            if new_id not in old_id_list:
                new_offer_string = new_shelf[new_id].pretty_str()
                print(colors.MAGENTA + '-' * 20 + 'OFFER' + '-' * 20 + colors.RESET)
                print(new_offer_string)

def show_price_change(old, new):
    old_shelf = shelve.open(old)
    new_shelf = shelve.open(new)
    if new_shelf and old_shelf is not None:
        old_id_list = old_shelf.keys()
        new_id_list = new_shelf.keys()
        for new_id in new_id_list:
            if new_id in old_id_list:
                price_difference = new_shelf[new_id].price - old_shelf[new_id].price
                if price_difference == 0:
                    print(f'{str(new_shelf[new_id])}{colors.BLUE} steady{colors.RESET}')
                    continue

                price_color_code = ''
                price_header = ''
                if price_difference < 0:
                    price_header = 'DOWN'
                    price_color_code = colors.GREEN
                else:
                    price_header = 'UP'
                    price_color_code = colors.RED

                new_offer_string = new_shelf[new_id].pretty_str()
                print(price_color_code + '-' * 20 + price_header + '-' * 20 + colors.RESET)
                print(new_offer_string)

if __name__ == "__main__":
    show_price_change("data/snapshot_lodz_5_2020_07_14/moto_shelf", "data/snapshot_lodz_5_2020_07_15/moto_shelf")
    show_new_offers("data/snapshot_lodz_5_2020_07_14/moto_shelf", "data/snapshot_lodz_5_2020_07_15/moto_shelf")
