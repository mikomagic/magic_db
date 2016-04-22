#!/usr/bin/python

import sys
import os
import re
import urllib
import argparse

from cached_page import CachedPage
from card_detail import CardDetailReader
from card_detail import CardDetailParser
import languages
from card_item import CardItem
from magic_db import MagicDB
from logger import Log


class CardItemParser(object):
    def __init__(self):
        self.number_re = re.compile(r'"number">(\d+)</td>')
        self.multiverseid_re = re.compile(r'multiverseid=(\d+)') # part of href
        self.name_re = re.compile(r'>([^<]+)</a>') # anchor text
        self.artist_re = re.compile(r'"artist">([^<]*?)</td>')
        self.color_re = re.compile(r'"color">([^<]*?)</td>')
        self.rarity_re = re.compile(r'"rarity">(.)</td>')
        
    def parse(self, text):
        ci = CardItem()
        ci.number = int(self.number_re.search(text).group(1))
        ci.multiverseid = int(self.multiverseid_re.search(text).group(1))
        ci.name = self.name_re.search(text).group(1)
        ci.artist = self.artist_re.search(text).group(1)
        ci.color = self.color_re.search(text).group(1)
        ci.rarity = self.rarity_re.search(text).group(1)
        return ci


class CheckList(object):
    def __init__(self):
        self.card_items = []

    def __link_back_sides(self):
        prev_ci = CardItem()
        prev_was_double = False
        for ci in self.card_items:
            if ci.number == prev_ci.number:
                if not prev_was_double:
                    prev_was_double = True
                    prev_ci.link_back_side(ci)
            else:
                prev_was_double = False
                prev_ci = ci

    def __build_index_by_number(self):
        by_number = {}
        for ci in self.card_items:
            if ci.number in by_number:
                if not ci.front_side:
                    Log.warn("number collision of %s and %s" % (ci, by_number[ci.number]))
                else:
                    pass # skip
            else:
                by_number[ci.number] = ci
        return by_number
        
    def __find_clashing_ids(self):
        all_ids = set()
        clashing_ids = set()
        for ci in self.card_items:
            if ci.multiverseid in all_ids:
                clashing_ids.add(ci.multiverseid)
            else:
                all_ids.add(ci.multiverseid)
        return clashing_ids

    def __fix_variations(self):
        by_number = self.__build_index_by_number()
        card_detail_parser = CardDetailParser()
        clashing_ids = self.__find_clashing_ids()
        for primary_id in clashing_ids:
            text = CardDetailReader(primary_id).read()
            variations = card_detail_parser.parse_variations(text)
            for id in variations:
                text = CardDetailReader(id).read()
                number = card_detail_parser.parse_card_number(text)
                card = by_number[number]
                assert card.multiverseid == primary_id # not yet fixed
                if card.multiverseid != id:
                    card.multiverseid = id
                    Log.debug("fixed multiverseid of %s" % card)
        
    def clean_up(self):
        self.__link_back_sides()
        self.__fix_variations()
        

class CheckListParser(object):
    def __init__(self):
        self.next_page_re = re.compile(r'<a href="[^"]+page=(\d+)[^"]+">&nbsp;&gt;</a>')
        self.num_results_re = re.compile(r'SEARCH:[^\(]*\((\d+)\)')
        self.card_item_re = re.compile(r'<tr class="cardItem">(.*?)</tr>')
        
    def parse_next_page(self, text):
        m = self.next_page_re.search(text)
        return int(m.group(1)) if m else None
    
    def parse_num_results(self, text):
        return int(self.num_results_re.search(text).group(1))

    def get_card_item_iter(self, text):
        return self.card_item_re.finditer(text)


class CheckListReader(object):
    def __init__(self, set_name):
        self.set_name = set_name
        self.num_results = None
        self.check_list = CheckList()
        self.__page_parser = CheckListParser()
        self.__card_item_parser = CardItemParser()
        self.__cur_page = 0

    def __read_page(self):
        params = {'output' : 'checklist',
                  'set'    : '["' + self.set_name + '"]',
                  'page'   : self.__cur_page,
                  'sort'   : 'cn+' }
        url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?' + urllib.urlencode(params)
        set_name = self.set_name.lower().replace(" ", "_")
        filename = ("%s_checklist_page_%s.html" % (set_name, self.__cur_page))
        return CachedPage(filename, url).read()
 
    def __parse_page(self, text):
        if self.num_results is None:
            self.num_results = self.__page_parser.parse_num_results(text)
        for m in self.__page_parser.get_card_item_iter(text):
            card_item = self.__card_item_parser.parse(m.group(1))
            self.check_list.card_items.append(card_item)
        next_page = self.__page_parser.parse_next_page(text)
        assert next_page is None or next_page == self.__cur_page + 1
        self.__cur_page = next_page

    def read(self):
        while self.__cur_page is not None:
            text = self.__read_page()
            self.__parse_page(text)
        return self.check_list

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape gatherer for one set.')
    parser.add_argument('--lang', help='translations to scrape; example: --lang=de,fr')
    parser.add_argument('-d', action="store_true", help='print debug logs')
    parser.add_argument('set_name', help='full name of Magic set to add or update (e.g., "Magic Origins")')
    return parser.parse_args()
    

def main():
    args = parse_args()
    Log.log_level = Log.DEBUG if args.d else Log.INFO
    
    reader = CheckListReader(args.set_name)
    check_list = reader.read()
    check_list.clean_up()
    
    db = MagicDB()
    db.add_from_check_list(check_list.card_items)

    lang = args.lang.split(',') if args.lang else languages.ALL_LANGS
    for ci in db.check_list:
        if not ci.has_translations():
            translations = languages.TranslationFinder(ci.multiverseid, lang).read()
            translations.associate_and_add_to_db(db)

    print "=" * 80
    print "Final list:"
    print "=" * 80
    for ci in check_list.card_items:
        print db.get(ci.translations['de'])


if __name__ == "__main__":
    main()

