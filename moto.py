class motorcycle_offer:
    def __init__(self, model_name, capacity_cm3, price, currency, url, body, mileage, year):
        self.model_name = str(model_name)
        self.capacity_cm3 = int(capacity_cm3) if capacity_cm3 is not None else None
        self.price = int(price) if price is not None else None
        self.url = str(url)
        self.body = str(body)
        self.mileage = int(mileage) if mileage is not None else None
        self.currency = str(currency)
        self.year = str(year)

    def __str__(self):
        return f'{self.model_name}, {self.capacity_cm3} cm3, {self.year}, {self.price} {self.currency}'

    def pretty_str(self):
        result = []
        header_width = 40
        filler = int((header_width - len(self.model_name)) / 2)
        header_string = '-' * filler + self.model_name + '-' * filler + '\n'
        result.append(header_string)
        result.append(f'{self.capacity_cm3} cm3\n')
        result.append(f'{self.mileage} km\n')
        result.append(f'{self.year}')
        result.append(f'{self.price} {self.currency}\n')
        result.append(f'{self.url}\n')
        result.append('\n')
        return ''.join(result)