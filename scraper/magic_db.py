

class MagicDB:
    def __init__(self):
        self.all_cards = {}
        self.check_list = []

    def add_from_check_list(self, check_list):
        self.check_list = [ ci for ci in check_list ]
        for ci in self.check_list:
            self.all_cards[ci.multiverseid] = ci

    def add(self, ci):
        self.all_cards[ci.multiverseid] = ci

    def get(self, multiverseid):
        return self.all_cards[multiverseid]

    def find_by_number(self, number):
        for ci in self.check_list:
            if ci.number == number:
                return ci
