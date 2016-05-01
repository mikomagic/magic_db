import logging
from checklist import Checklist
from languages import Translations
from card_detail import CardDetail

log = logging.getLogger(__name__)


class SetScraper(dict):
    def __init__(self, set_code, set_name, langs):
        self.set_code = set_code
        self.set_name = set_name
        self.langs = langs
        self.checklist = []

    def scrape(self):
        self.checklist = Checklist(self.set_code, self.set_name).create()
        for card in self.checklist:
            card.equivalent_to = CardDetail(card.multiverseid).get_equivalence()
            if card.equivalent_to:
                log.debug("%s is equivalent to %d", card, card.equivalent_to)
            self.add(card)
        if self.langs:
            for card in self.checklist:
                if not card.has_translations():
                    Translations(card.multiverseid, self.langs).associate_and_add(self)
        return self

    def add(self, card):
        assert not card.multiverseid in self
        self[card.multiverseid] = card

    def get(self, multiverseid):
        return self[multiverseid]

    def find_by_number(self, number):
        cards = []
        for card in self.checklist:
            if card.number == number:
                cards.append(card)
        assert len(cards) == 1
        return cards[0]
