import re
import urllib
import logging
from cached_page import CachedPage

log = logging.getLogger(__name__)

variation_re = re.compile(r'id="(\d+)" class="variationLink"')
card_number_re = re.compile(r'Card Number:.*?(\d+)</div>', flags=re.DOTALL)
equivalence_re = re.compile(r'otherSetsValue">\s*<a href="Details.aspx\?multiverseid=(\d+)">', flags=re.DOTALL)
card_component_re = re.compile(r'cardComponent(\d)" class=.*?multiverseid=(\d+)', flags=re.DOTALL)

class CardDetail(object):
    def __init__(self, multiverseid):
        self.multiverseid = multiverseid
        self.__text = None

    def __get_text(self):
        if not self.__text:
            params = { 'multiverseid' : self.multiverseid }
            url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?' + urllib.urlencode(params)
            filename = "detail_%d.html" % (self.multiverseid)
            self.__text = CachedPage(filename, url).read()
        return self.__text

    def get_variations(self):
        variations = []
        for m in variation_re.finditer(self.__get_text()):
            v = int(m.group(1))
            assert not v in variations
            variations.append(v)
        log.debug("variations of %d: %s" % (self.multiverseid, variations))
        return variations

    def get_card_number(self):
        m = card_number_re.search(self.__get_text())
        return int(m.group(1))

    def get_equivalence(self):
        m = equivalence_re.search(self.__get_text())
        if m:
            eq = int(m.group(1))
            if eq != self.multiverseid:
                return eq
        return None

    def get_card_components(self):
        comps = {}
        for m in card_component_re.finditer(self.__get_text()):
            comps[int(m.group(1))] = int(m.group(2))
        log.debug("card components for %d: %s" % (self.multiverseid, comps))
        return comps
