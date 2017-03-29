#!/usr/bin/env python
from __future__ import unicode_literals

import requests
import argparse
import os
from bs4 import BeautifulSoup
from functools import reduce


class Deck(object):
    def __init__(self, page_url, element, banlist):
        self.name = element.find('h4').text
        self.link = page_url + '#' + element.get('id')
        self.banlist = banlist
        self.card_counts = dict(
            (card.select_one('.card-name').text, int(card.select_one('.card-count').text))
            for card in element.select('.row')
        )

    @property
    def banned_cards(self):
        return dict(
            (k, v) for k, v in self.card_counts.items() if k in self.banlist
        )

    @property
    def num_banned_cards(self):
        return reduce(
            lambda a, b: a + b,
            (v for k, v in self.banned_cards.items())
        )

    @property
    def num_distinct_banned_cards(self):
        return len(self.banned_cards.keys())

    def prettify(self):
        header = '[{}]({})'.format(self.name, self.link)
        separator_line = '=' * len(header)
        lines = [
            separator_line,
            header,
            separator_line,
            'Loses {} total cards ({} distinct)'.format(self.num_banned_cards, self.num_distinct_banned_cards),
        ] + [
            '-{count} {name}'.format(count=v, name=k)
            for k, v in sorted(self.banned_cards.items(), key=lambda entry: -entry[1])
        ] + [
            separator_line
        ]
        return '\n'.join('|' + l.ljust(len(header)) + '|' for l in lines)

    def __repr__(self):
        return '{}'.format(self.card_counts)


def get_least_affected_decks(page_url, banlist, num=10):
    page = BeautifulSoup(requests.get(page_url).content, 'html.parser')
    decks = [
        Deck(page_url, element, banlist)
        for element in page.select('.deck-group')
    ]
    decks = sorted(decks, key=lambda d: d.num_banned_cards)
    return decks[0:num]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--banlist-file',
        help='file containing banned cards',
        default=os.path.join('data', 'banlist.txt'),
    )
    parser.add_argument(
        '--url',
        help='WOTC url containing tier 2 deck lists to search through',
        default='http://magic.wizards.com/en/events/coverage/gppoa17/9-32-decklists-2017-03-19',
    )
    parser.add_argument(
        '--num-decks',
        help='number of decks to display',
        type=int,
        default=10,
    )

    args = parser.parse_args()

    banlist = set()
    with open(args.banlist_file) as f:
        for c in f.readlines():
            banlist.add(c.strip())

    decks = get_least_affected_decks(args.url, banlist, args.num_decks)
    for deck in decks:
        print deck.prettify()
