class motorcycle_offer:
    def __init__(self, model_name, capacity_cm3, price, currency, url, body, mileage, year, moto_id):
        self.model_name = str(model_name)
        self.capacity_cm3 = int(capacity_cm3) if capacity_cm3 is not None else None
        self.price = int(price) if price is not None else None
        self.url = str(url)
        self.body = str(body)
        self.mileage = int(mileage) if mileage is not None else None
        self.currency = str(currency)
        self.year = str(year)
        self.moto_id = int(moto_id) if moto_id is not None else None
        self.description = None

    def __str__(self):
        result = f'{self.model_name}'
        if self.capacity_cm3 != None:
            result += f' {self.capacity_cm3} cm3'
        return result

    def pretty_str(self):
        result = []
        result.append(f'{self.model_name}\n')
        result.append(f'{self.year}\n')
        result.append(f'{self.mileage} km\n')
        result.append(f'{self.capacity_cm3} cm3\n')
        result.append(f'{self.price} {self.currency}\n')
        result.append(f'{self.description}\n')
        result.append(f'{self.url}\n')
        return ''.join(result)