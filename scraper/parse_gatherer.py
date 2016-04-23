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
from card_item import Card
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
        card = Card()
        card.number = int(self.number_re.search(text).group(1))
        card.multiverseid = int(self.multiverseid_re.search(text).group(1))
        card.name = self.name_re.search(text).group(1)
        card.artist = self.artist_re.search(text).group(1)
        card.color = self.color_re.search(text).group(1)
        card.rarity = self.rarity_re.search(text).group(1)
        return card


class CheckList(object):
    def __init__(self):
        self.card_items = []

    def __link_back_faces(self):
        prev_card = Card()
        for card in self.card_items:
            if card.number == prev_card.number:
                if not prev_card.back_face:
                    prev_card.link_back_face(card)
            else:
                prev_card = card

    def __build_index_by_number(self):
        by_number = {}
        for card in self.card_items:
            if card.number in by_number:
                if not card.front_face:
                    Log.warn("number collision of %s and %s" % (card, by_number[card.number]))
                else:
                    pass # skip
            else:
                by_number[card.number] = card
        return by_number

    def __find_clashing_ids(self):
        all_ids = set()
        clashing_ids = set()
        for card in self.card_items:
            if card.multiverseid in all_ids:
                clashing_ids.add(card.multiverseid)
            else:
                all_ids.add(card.multiverseid)
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
        self.__link_back_faces()
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
    for card in db.check_list:
        if not card.has_translations():
            translations = languages.TranslationFinder(card.multiverseid, lang).read()
            translations.associate_and_add_to_db(db)

    print "=" * 80
    print "Final list:"
    print "=" * 80
    for card in check_list.card_items:
        print card.translations['de']


if __name__ == "__main__":
    main()
