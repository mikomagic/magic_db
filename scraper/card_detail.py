import re
import urllib
from cached_page import CachedPage


class CardDetailParser(object):
    def __init__(self):
        self.variation_re = re.compile(r'id="(\d+)" class="variationLink"')
        self.card_number_re = re.compile(r'Card Number:.*?(\d+)</div>', flags=re.DOTALL)

    def parse_variations(self, text):
        variations = []
        for m in self.variation_re.finditer(text):
            variations.append(int(m.group(1)))
        return variations

    def parse_card_number(self, text):
        return int(self.card_number_re.search(text).group(1))


class CardDetailReader(object):
    def __init__(self, multiverseid):
        self.multiverseid = multiverseid

    def read(self):
        params = { 'multiverseid' : self.multiverseid }
        url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?' + urllib.urlencode(params)
        filename = "detail_%d.html" % (self.multiverseid)
        return CachedPage(filename, url).read()
