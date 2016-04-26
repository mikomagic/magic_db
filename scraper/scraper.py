from check_list import CheckList
from magic_db import MagicDB
from languages import TranslationFinder

class SetScraper(object):
    def __init__(self, set_name, langs):
        self.set_name = set_name
        self.langs = langs

    def scrape(self):
        check_list_cards = CheckList(self.set_name).get()
        db = MagicDB()
        db.add_from_check_list(check_list_cards)
        if self.langs:
            for card in check_list_cards:
                if not card.has_translations():
                    translations = TranslationFinder(card.multiverseid, self.langs).read()
                    translations.associate_and_add_to_db(db)
        return db
