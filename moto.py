from color_codes import colors

class moto_attribute:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return f'{self.name}: {self.value}'

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
        self.attributes = []

    def __eq__(self, other):
        if other is not motorcycle_offer:
            return False
        else:
            return self.moto_id == other.moto_id

    def __str__(self):
        result = f'{self.model_name}'
        if self.capacity_cm3 != None:
            result += f' {self.capacity_cm3}cm3'
        return result

    def pretty_str(self, attributes=False):
        result = []
        result.append(colors.MAGENTA + f'{self.model_name}\n' + colors.RESET)
        result.append(f'{self.year}\n')
        result.append(f'{self.mileage} km\n')
        result.append(colors.MAGENTA + f'{self.capacity_cm3} cm3\n' + colors.RESET)
        result.append(colors.CYAN + f'{self.price} {self.currency}\n' + colors.RESET)
        result.append(f'{self.description}\n')
        result.append(f'{self.url}\n')
        if attributes:
            for att in self.attributes:
                result.append(f'{str(att)}\n')
        return ''.join(result)