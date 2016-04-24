#!/usr/bin/python

import sys
import os
import re
import urllib
import argparse

import languages
from card import Card
from check_list import CheckList
from magic_db import MagicDB
from logger import Log


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape gatherer for one set.')
    parser.add_argument('--lang', help='translations to scrape; example: --lang=de,fr')
    parser.add_argument('-d', action="store_true", help='print debug logs')
    parser.add_argument('set_name', help='full name of Magic set to add or update (e.g., "Magic Origins")')
    return parser.parse_args()


def main():
    args = parse_args()
    Log.log_level = Log.DEBUG if args.d else Log.INFO

    check_list_cards = CheckList(args.set_name).get()
    db = MagicDB()
    db.add_from_check_list(check_list_cards)

    lang = args.lang.split(',') if args.lang else languages.ALL_LANGS
    for card in check_list_cards:
        if not card.has_translations():
            translations = languages.TranslationFinder(card.multiverseid, lang).read()
            translations.associate_and_add_to_db(db)

    print "=" * 80
    print "Final list:"
    print "=" * 80
    for card in check_list_cards:
        print card.translations['de']


if __name__ == "__main__":
    main()
