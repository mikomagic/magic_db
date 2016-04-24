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
    parser.add_argument('-l', '--lang', help='translations to scrape (none|all|de,fr ...)')
    parser.add_argument('-d', '--debug', action="store_true", help='print debug logs')
    parser.add_argument('set_name', help='full name of Magic set to add or update (e.g., "Magic Origins")')
    return parser.parse_args()


def main():
    args = parse_args()
    Log.log_level = Log.DEBUG if args.debug else Log.INFO

    check_list_cards = CheckList(args.set_name).get()
    db = MagicDB()
    db.add_from_check_list(check_list_cards)

    langs = []
    if args.lang == 'all':
        langs = languages.ALL_LANGS
    elif args.lang != 'none':
        langs = args.lang.split(',')
        for t in langs:
            if t not in languages.ALL_LANGS:
                print 'Unknown language "%s".' % t
                sys.exit(2)
    if langs:
        for card in check_list_cards:
            if not card.has_translations():
                translations = languages.TranslationFinder(card.multiverseid, langs).read()
                translations.associate_and_add_to_db(db)

    print "=" * 80
    print "Final list:"
    print "=" * 80
    for card in check_list_cards:
        print "%-50s%s" % (card, card.translations[langs[0]].name if langs else "")


if __name__ == "__main__":
    main()
