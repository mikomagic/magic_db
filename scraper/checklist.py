import urllib
import re
import logging

from card import Card
from card_detail import CardDetail
from cached_page import CachedPage
from multi_page_scraper import MultiPageScraper

log = logging.getLogger(__name__)

# on whole checklist page:
next_page_re = re.compile(r'<a href="[^"]+page=(\d+)[^"]+">&nbsp;&gt;</a>')
num_results_re = re.compile(r'SEARCH:[^\(]*\((\d+)\)')
card_item_re = re.compile(r'<tr class="cardItem">(.*?)</tr>')

# on individual card items:
number_re = re.compile(r'"number">(\d+)</td>')
multiverseid_re = re.compile(r'multiverseid=(\d+)') # part of href
name_re = re.compile(r'>([^<]+)</a>') # anchor text
artist_re = re.compile(r'"artist">([^<]*?)</td>')
color_re = re.compile(r'"color">([^<]*?)</td>')
rarity_re = re.compile(r'"rarity">(.)</td>')


class ChecklistScraper(MultiPageScraper):
    def __init__(self, set_code, set_name):
        super(ChecklistScraper, self).__init__(next_page_re)
        self.set_code = set_code
        self.set_name = set_name
        self.num_results = None
        self.cards = []

    def __parse_card_item(self, text):
        card = Card()
        card.multiverseid = int(multiverseid_re.search(text).group(1))
        card.set_code = self.set_code
        card.number = int(number_re.search(text).group(1))
        card.name = name_re.search(text).group(1)
        card.artist = artist_re.search(text).group(1)
        card.color = color_re.search(text).group(1)
        card.rarity = rarity_re.search(text).group(1)
        return card

    def _read_page(self, page):
        params = {'output' : 'checklist',
                  'set'    : '["' + self.set_name + '"]',
                  'page'   : page,
                  'sort'   : 'cn+' }
        url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?' + urllib.urlencode(params)
        set_name = self.set_name.lower().replace(" ", "_")
        filename = ("%s_checklist_page_%s.html" % (set_name, page))
        return CachedPage(filename, url).read()

    def _parse_page(self, text):
        if self.num_results is None:
            self.num_results = int(num_results_re.search(text).group(1))
        prev_number = self.cards[-1].number if self.cards else 0
        for m in card_item_re.finditer(text):
            card = self.__parse_card_item(m.group(1))
            assert card.number >= prev_number, "cards out of order at %s" % card
            assert card.number <= prev_number + 1, "missing cards before %s" % card
            self.cards.append(card)
            prev_number = card.number

    def scrape(self):
        self._scrape()
        return self.cards


class Checklist(object):
    """Constructs a cleaned up version of a checklist search result for the
    chosen set.  Two issues are fixed:
    - checklist shows front and back faces of cards as individual
      card items; we link them via Card.link_back_face()
    - checklist shows variations of a card with different collector's
      numbers, but with the same multiverseid (of a seemingly random
      instance); we fix the multiverseid of each such card.
    """
    def __init__(self, set_code, set_name):
        self.set_code = set_code
        self.set_name = set_name
        self.cards = None

    def __link_back_faces(self):
        prev_card = Card()
        prev_card.number = 0
        for i, card in enumerate(self.cards):
            if card.number == prev_card.number:
                if card.multiverseid != prev_card.multiverseid:
                    # assume double-sided card
                    comps = CardDetail(prev_card.multiverseid).get_card_components()
                    assert len(comps) == 2 and comps[0] != comps[1]
                    faces = { card.multiverseid : card, prev_card.multiverseid : prev_card }
                    # ordering may be reversed; fix
                    self.cards[i-1] = prev_card = faces[comps[0]]
                    self.cards[i] = card = faces[comps[1]]
                    prev_card.link_back_face(card)
            else:
                assert prev_card.number + 1 == card.number
            prev_card = card

    def __find_clashing_cards(self):
        all_cards = {} # multiverseid -> Card
        clashing_cards = {} # multiverseid -> [ Card ]
        for card in self.cards:
            if card.multiverseid in clashing_cards:
                clashing_cards[card.multiverseid].append(card)
            elif card.multiverseid in all_cards:
                clashing_cards[card.multiverseid] = [all_cards[card.multiverseid], card]
            else:
                all_cards[card.multiverseid] = card
        return clashing_cards

    def __pick_matching_card(self, candidates, card_number):
        match = -1
        for i, card in enumerate(candidates):
            if card.number == card_number:
                if match != -1:
                    assert candidates[match] == card # fully equivalent
                match = i
        return candidates.pop(match)

    def __fix_variations(self):
        clashing_cards = self.__find_clashing_cards()
        for clashing_id, clashing_set in clashing_cards.iteritems():
            for variation_id in CardDetail(clashing_id).get_variations():
                card_number = CardDetail(variation_id).get_card_number()
                card = self.__pick_matching_card(clashing_set, card_number)
                assert card.number == card_number
                assert card.multiverseid == clashing_id # not yet fixed
                if card.multiverseid != variation_id:
                    card.multiverseid = variation_id
                    log.debug("fixed multiverseid of %s" % card)
            assert not clashing_set # all found

    def create(self):
        if not self.cards:
            self.cards = ChecklistScraper(self.set_code, self.set_name).scrape()
            self.__link_back_faces()
            self.__fix_variations()
        return self.cards
