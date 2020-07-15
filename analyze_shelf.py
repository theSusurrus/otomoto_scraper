from moto import motorcycle_offer
import shelve
import re
import matplotlib.pyplot as plt

def analyze_shelf(shelf_name, models=['bandit'], capacity=(1240, 1260), count_new=False, new_threshold=500):
    regex = f"({'|'.join(models)})".lower()
    shelf = shelve.open(shelf_name)
    if shelf is not None:
        prices = []
        mileages = []
        id_list = shelf.keys()
        for index, id in enumerate(id_list):
            moto = shelf[id]
            match = re.search(regex, moto.model_name.lower())
            capacity_match = None
            if moto.capacity_cm3 is not None:
                capacity_match = moto.capacity_cm3 > capacity[0] and moto.capacity_cm3 < capacity[1]
            if match is not None and capacity_match:
                print(moto.model_name)
                print(f'{moto.price}PLN')
                print()
                if moto.price is not None and moto.mileage is not None:
                    if not count_new and moto.mileage < new_threshold:
                        continue
                    mileages.append(moto.mileage)
                    prices.append(moto.price)
    
    if len(mileages) and len(prices):
        plt.scatter(mileages, prices)
        plt.title(f"Prices vs mileages for models: {', '.join(models)}")
        plt.show()

if __name__ == "__main__":
    analyze_shelf(
        "data/snapshot_lodz_100_2020_07_15/moto_shelf",
        models=['cbf'],
        capacity=(580, 620),
        count_new=True
        )
