#!/usr/bin/env python
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup
import sys
import argparse


def dump_banlist_to_file(page_url, output_file):
    ban_list = sorted(get_banlist(page_url))
    print 'Writing banlist to {}'.format(output_file)
    with open(output_file, 'w') as f:
        for c in ban_list:
            f.write(c + '\n')


def get_banlist(page_url):
    card_types = (
        'creature',
        'instant',
        'sorcery',
        'enchantment',
        'artifact',
        'planeswalker',
    )
    print 'Fetching from {}'.format(page_url)
    page = BeautifulSoup(requests.get(page_url).content, 'html.parser')
    banned_cards = set()
    for card_type in card_types:
        banned_cards_of_type = set(
            a.text for a in page.select(
                '.deck-list-text .sorted-by-{} .card-name a'.format(card_type)
            )
        )
        print 'Found {} banned {} cards'.format(len(banned_cards_of_type), card_type)
        banned_cards = banned_cards.union(banned_cards_of_type)
    print 'Found {} banned cards'.format(len(banned_cards))
    return banned_cards


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        help='WOTC page containing the decklists to ban',
        default='http://magic.wizards.com/en/events/coverage/gppoa17/top-8-decklists-2017-03-19',
    )
    parser.add_argument(
        '--output-file',
        help='File to write banlist to',
        default='banlist.txt',
    )
    args = parser.parse_args()
    dump_banlist_to_file(args.url, args.output_file)
