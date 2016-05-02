import re
import urllib
from cached_page import CachedPage
from card import Card
from card_detail import CardDetail
from multi_page_scraper import MultiPageScraper

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

ALL_LANGS = [ v for k, v in LANG_DICT.iteritems() ] # excluding English

# whole language list page
next_page_re = re.compile(r'<a href="[^"]+page=(\d+)[^"]+">&nbsp;&gt;</a>')
num_results_re = re.compile(r'SEARCH:[^\(]*\((\d+)\)')
card_item_re = re.compile(r'<tr class="cardItem .*?>(.*?)</tr>', flags=re.DOTALL)

# individual card item
multiverseid_re = re.compile(r'multiverseid=(\d+)')
name_re = re.compile(r'([^<>]+)</a>')
language_re = re.compile(r'<td style="text-align: center;">\s+(.*?)\s+</td>', flags=re.DOTALL)

class LanguageListScraper(MultiPageScraper):
    def __init__(self, multiverseid, filter_languages):
        super(LanguageListScraper, self).__init__(next_page_re)
        self.multiverseid = multiverseid
        self.filter_languages = filter_languages

    def __parse_card_item(self, text):
        card = Card()
        card.multiverseid = int(multiverseid_re.search(text).group(1))
        card.name = name_re.search(text).group(1)
        card.language = LANG_DICT[language_re.search(text).group(1)]
        # other attributes are set by Card.add_translation()
        return card

    def _read_page(self, page):
        params = { 'multiverseid' : self.multiverseid,
                   'page'         : page }
        url = 'http://gatherer.wizards.com/Pages/Card/Languages.aspx?' + urllib.urlencode(params)
        filename = "languages_%d_%d.html" % (self.multiverseid, page)
        return CachedPage(filename, url).read()

    def _parse_page(self, text):
        for m in card_item_re.finditer(text):
            card = self.__parse_card_item(m.group(1))
            if card.language in self.filter_languages:
                self.translations.add(card)

    def scrape(self, translations):
        self.translations = translations
        self._scrape()


class Translations(object):
    """Either a single translation per language, in which case they are
    translations of the original card.  Or several translations per language,
    each for a variation of the original card.
    """
    def __init__(self, multiverseid, filter_languages):
        self.multiverseid = multiverseid
        self.filter_languages = filter_languages
        self.cards = {} # language -> [ Card ]
        self.__scraped = False

    def add(self, card):
        assert card.language in self.filter_languages
        self.cards.setdefault(card.language, []).append(card)

    def __associate_vector(self, cards, db):
        # It appears that the multiverseids of the foreign language variations
        # are at a fixed offset to the multiverseids of the corresponding English
        # variations.  Card number can help us verify this, though they are not
        # always unique (BFZ lands for example).
        variations_en = sorted(CardDetail(self.multiverseid).get_variations())
        cards_en = [db.get(v) for v in variations_en]
        cards.sort(key=lambda card: card.multiverseid)
        assert len(cards_en) == len(cards)
        offset = cards[0].multiverseid - cards_en[0].multiverseid
        prev_id = -1
        for card, card_en in zip(cards, cards_en):
            assert card.multiverseid > prev_id
            prev_id = card.multiverseid
            assert card.multiverseid - card_en.multiverseid == offset
            card.number = CardDetail(card.multiverseid).get_card_number()
            assert card_en.number == card.number
            # looks good
            card_en.add_translation(card)
            db.add(card)

    def __scrape(self):
        if not self.__scraped:
            scraper = LanguageListScraper(self.multiverseid, self.filter_languages)
            scraper.scrape(self)
            self.__scraped = True

    def associate_and_add(self, db):
        self.__scrape()
        for k, v in self.cards.iteritems():
            if len(v) == 1:
                db.get(self.multiverseid).add_translation(v[0])
                db.add(v[0])
            else:
                self.__associate_vector(v, db)
