import logging
from check_list import CheckList
from languages import TranslationFinder
from card_detail import CardDetail

log = logging.getLogger(__name__)


class SetScraper(dict):
    def __init__(self, set_code, set_name, langs):
        self.set_code = set_code
        self.set_name = set_name
        self.langs = langs
        self.check_list = []

    def scrape(self):
        self.check_list = CheckList(self.set_code, self.set_name).get()
        for card in self.check_list:
            card.equivalent_to = CardDetail(card.multiverseid).get_equivalence()
            if card.equivalent_to:
                log.debug("%s is equivalent to %d", card, card.equivalent_to)
            self.add(card)
        if self.langs:
            for card in self.check_list:
                if not card.has_translations():
                    translations = TranslationFinder(card.multiverseid, self.langs).read()
                    translations.associate_and_add(self)
        return self

    def add(self, card):
        assert not card.multiverseid in self
        self[card.multiverseid] = card

    def get(self, multiverseid):
        return self[multiverseid]

    def find_by_number(self, number):
        for card in self.check_list:
            if card.number == number:
                return card
