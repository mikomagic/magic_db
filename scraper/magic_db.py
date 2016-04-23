

class MagicDB:
    def __init__(self):
        self.all_cards = {}
        self.check_list = []

    def add_from_check_list(self, check_list):
        self.check_list = [ card for card in check_list ]
        for card in self.check_list:
            self.all_cards[card.multiverseid] = card

    def add(self, card):
        self.all_cards[card.multiverseid] = card

    def get(self, multiverseid):
        return self.all_cards[multiverseid]

    def find_by_number(self, number):
        for card in self.check_list:
            if card.number == number:
                return card
