from moto import motorcycle_offer
import shelve

def print_shelf(shelf_name):
    shelf = shelve.open(shelf_name)
    if shelf is not None:
        id_list = shelf.keys()
        for index, id in enumerate(id_list):
            moto = shelf[id]
            moto_str = shelf[id].pretty_str()
            print(moto_str)

if __name__ == "__main__":
    print_shelf("data/snapshot_kolo_5_2020_07_14/moto_shelf")