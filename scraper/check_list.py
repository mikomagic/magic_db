import urllib
import re

from logger import Log
from card import Card
from card_detail import CardDetail
from cached_page import CachedPage


# whole check_list page
next_page_re = re.compile(r'<a href="[^"]+page=(\d+)[^"]+">&nbsp;&gt;</a>')
num_results_re = re.compile(r'SEARCH:[^\(]*\((\d+)\)')
card_item_re = re.compile(r'<tr class="cardItem">(.*?)</tr>')

# individual card_item
number_re = re.compile(r'"number">(\d+)</td>')
multiverseid_re = re.compile(r'multiverseid=(\d+)') # part of href
name_re = re.compile(r'>([^<]+)</a>') # anchor text
artist_re = re.compile(r'"artist">([^<]*?)</td>')
color_re = re.compile(r'"color">([^<]*?)</td>')
rarity_re = re.compile(r'"rarity">(.)</td>')


class CheckListScraper(object):
    '''Constructs a cleaned up version of a check_list search result for the
    chosen set.  Two issues are fixed:
    - check_list shows front and back faces of cards as individual
      card items; we link them via Card.link_back_face()
    - check_list shows variations of a card with different collector's
      numbers, but with the same multiverseid (of a seemingly random
      instance); we fix the multiverseid of each such card.
    '''
    def __init__(self, set_name):
        self.set_name = set_name
        self.num_results = None
        self.cards = []

    def __parse_card_item(self, text):
        card = Card()
        card.number = int(number_re.search(text).group(1))
        card.multiverseid = int(multiverseid_re.search(text).group(1))
        card.name = name_re.search(text).group(1)
        card.artist = artist_re.search(text).group(1)
        card.color = color_re.search(text).group(1)
        card.rarity = rarity_re.search(text).group(1)
        return card

    def __read_page(self, page):
        params = {'output' : 'checklist',
                  'set'    : '["' + self.set_name + '"]',
                  'page'   : page,
                  'sort'   : 'cn+' }
        url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?' + urllib.urlencode(params)
        set_name = self.set_name.lower().replace(" ", "_")
        filename = ("%s_checklist_page_%s.html" % (set_name, page))
        return CachedPage(filename, url).read()

    def __parse_page(self, text):
        if self.num_results is None:
            self.num_results = int(num_results_re.search(text).group(1))
        prev_number = self.cards[-1].number if self.cards else 0
        for m in card_item_re.finditer(text):
            card = self.__parse_card_item(m.group(1))
            assert card.number >= prev_number, "cards out of order at %s" % card
            assert card.number <= prev_number + 1, "missing cards before %s" % card
            self.cards.append(card)
            prev_number = card.number

    def __parse_next_page(self, text, cur_page):
        m = next_page_re.search(text)
        next_page = int(m.group(1)) if m else None
        assert next_page is None or next_page == cur_page + 1
        return next_page

    def scrape(self):
        page = 0
        while page is not None:
            text = self.__read_page(page)
            self.__parse_page(text)
            page = self.__parse_next_page(text, page)
        return self.cards


class CheckList(object):
    def __init__(self, set_name):
        self.cards = None
        self.set_name = set_name

    def __link_back_faces(self):
        prev_card = Card()
        for card in self.cards:
            if card.number == prev_card.number:
                if not prev_card.back_face:
                    prev_card.link_back_face(card)
            else:
                prev_card = card

    def __build_index_by_number(self):
        by_number = {}
        for card in self.cards:
            if card.number in by_number:
                assert card.front_face, "number collision of %s and %s" % (card, by_number[card.number])
                # skip back face
            else:
                by_number[card.number] = card
        return by_number

    def __find_clashing_ids(self):
        all_ids = set()
        clashing_ids = set()
        for card in self.cards:
            if card.multiverseid in all_ids:
                clashing_ids.add(card.multiverseid)
            else:
                all_ids.add(card.multiverseid)
        return clashing_ids

    def __fix_variations(self):
        by_number = self.__build_index_by_number()
        for primary_id in self.__find_clashing_ids():
            for variation_id in CardDetail(primary_id).get_variations():
                card = by_number[CardDetail(variation_id).get_card_number()]
                assert card.multiverseid == primary_id # not yet fixed
                if card.multiverseid != variation_id:
                    card.multiverseid = variation_id
                    Log.debug("fixed multiverseid of %s" % card)

    def get(self):
        if not self.cards:
            self.cards = CheckListScraper(self.set_name).scrape()
            self.__link_back_faces()
            self.__fix_variations()
        return self.cards