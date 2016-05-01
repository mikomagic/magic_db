#!/usr/bin/python

import sys
import os
import argparse
import logging

from scraper.scraper import SetScraper
from scraper.languages import ALL_LANGS


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape gatherer for one set.')
    parser.add_argument('-l', '--lang', default='none', help='translations to scrape (none|all|de,fr ...)')
    parser.add_argument('set_code', help='three-letter code of set to add or update (e.g., "ORI")')
    parser.add_argument('set_name', help='full name of set to scrape (e.g., "Magic Origins")')
    args = parser.parse_args()
    langs = []
    if args.lang == 'all':
        langs = ALL_LANGS
    elif args.lang != 'none':
        langs = args.lang.split(',')
        for t in langs:
            if t not in ALL_LANGS:
                print 'Unknown language "%s".' % t
                sys.exit(2)
    return args, langs


def main():
    args, langs = parse_args()
    logging.basicConfig(filename=".scrape.log", filemode="w", level=logging.DEBUG)
    db = SetScraper(args.set_code, args.set_name, langs).scrape()

    print "=" * 80
    print "Final list:"
    print "=" * 80
    for card in db.check_list:
        print "%-50s%s" % (card, card.translations[langs[0]].name if langs else "")


if __name__ == "__main__":
    main()
