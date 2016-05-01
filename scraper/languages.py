import re
import urllib
from cached_page import CachedPage
from card import Card
from card_detail import CardDetail

LANG_DICT = {
    'Chinese Traditional' : 'ct',
    'German'              : 'de',
    'French'              : 'fr',
    'Italian'             : 'it',
    'Japanese'            : 'jp',
    'Korean'              : 'kr',
    'Portuguese (Brazil)' : 'pt',
    'Russian'             : 'ru',
    'Chinese Simplified'  : 'cs',
    'Spanish'             : 'sp' }

ALL_LANGS = [ v for k, v in LANG_DICT.iteritems() ]

class LanguageItemParser(object):
    def __init__(self, filter_languages):
        self.multiverseid_re = re.compile(r'multiverseid=(\d+)')
        self.name_re = re.compile(r'([^<>]+)</a>')
        self.language_re = re.compile(r'<td style="text-align: center;">\s+(.*?)\s+</td>', flags=re.DOTALL)

    def parse(self, text):
        card = Card()
        card.multiverseid = int(self.multiverseid_re.search(text).group(1))
        card.name = self.name_re.search(text).group(1)
        card.language = LANG_DICT[self.language_re.search(text).group(1)]
        # other attributes are set by Card.add_translation()
        return card


class LanguageListParser(object):
    def __init__(self):
        self.next_page_re = re.compile(r'<a href="[^"]+page=(\d+)[^"]+">&nbsp;&gt;</a>')
        self.num_results_re = re.compile(r'SEARCH:[^\(]*\((\d+)\)')
        self.card_item_re = re.compile(r'<tr class="cardItem .*?>(.*?)</tr>', flags=re.DOTALL)

    def parse_next_page(self, text):
        m = self.next_page_re.search(text)
        return int(m.group(1)) if m else None

    def parse_num_results(self, text):
        return int(self.num_results_re.search(text).group(1))

    def get_card_item_iter(self, text):
        return self.card_item_re.finditer(text)


class Translations(object):
    '''Either a single translation per language, in which case they are
        translations of the original card.  Or, several translations
        per language, each for a variation of the original card.

    '''
    def __init__(self, multiverseid):
        self.multiverseid = multiverseid
        self.cards = {}

    def add(self, translated_item):
        self.cards.setdefault(translated_item.language, []).append(translated_item)

    def __associate_via_card_number(self, cards, db):
        for card in cards:
            number = CardDetail(card.multiverseid).get_card_number()
            card_en = db.find_by_number(number)
            card_en.add_translation(card)
            db.add(card)

    def associate_and_add_to_db(self, db):
        for k, v in self.cards.iteritems():
            if len(v) == 1:
                db.get(self.multiverseid).add_translation(v[0])
                db.add(v[0])
            else:
                self.__associate_via_card_number(v, db)



class TranslationFinder(object):
    def __init__(self, multiverseid, filter_languages=ALL_LANGS):
        self.filter_languages = filter_languages
        self.multiverseid = multiverseid
        self.translations = Translations(multiverseid)
        self.__page_parser = LanguageListParser()
        self.__item_parser = LanguageItemParser(filter_languages)
        self.__cur_page = 0

    def __read_page(self):
        params = { 'multiverseid' : self.multiverseid,
                   'page'         : self.__cur_page }
        url = 'http://gatherer.wizards.com/Pages/Card/Languages.aspx?' + urllib.urlencode(params)
        filename = "languages_%d_%d.html" % (self.multiverseid, self.__cur_page)
        return CachedPage(filename, url).read()

    def __parse_page(self, text):
        for m in self.__page_parser.get_card_item_iter(text):
            card_item = self.__item_parser.parse(m.group(1))
            if card_item.language in self.filter_languages:
                self.translations.add(card_item)
        next_page = self.__page_parser.parse_next_page(text)
        assert next_page is None or next_page == self.__cur_page + 1
        self.__cur_page = next_page

    def read(self):
        while self.__cur_page is not None:
            text = self.__read_page()
            self.__parse_page(text)
        return self.translations
