#!/usr/bin/env python
from __future__ import unicode_literals

import requests
import sys
import os
from bs4 import BeautifulSoup


BASE_URL = 'http://gatherer.wizards.com'


STARTING_URL = BASE_URL + '/Pages/Search/Default.aspx?action=advanced&format=+[%22Standard%22]'


def dump_standard_cards_to_file(output_file):
    cards = get_all_cards()
    print 'Writing {} cards to {}'.format(len(cards), output_file)
    with open(output_file, 'w') as f:
        for c in cards:
            f.write(c + '\n')


def get_all_cards():
    page_url = STARTING_URL
    cards = []
    while page_url:
        print 'Fetching from {}'.format(page_url)
        page = BeautifulSoup(requests.get(page_url).content, 'html.parser')
        new_cards = extract_cards(page)
        print 'Found {} cards'.format(len(new_cards))
        cards += new_cards
        page_url = extract_next_page_link(page)
    return cards


def extract_cards(page):
    return [a.text for a in page.select('.cardInfo a')]


def extract_next_page_link(page):
    return next(
        (
            BASE_URL + a.get('href') for a in page.select('.pagingcontrols a')
            if '>' in a.text and not '>>' in a.text
        ),
        None
    )


if __name__ == '__main__':
    try:
        output_file = sys.argv[1]
    except IndexError:
        output_file = os.path.join('data', 'standard_cards.txt')
    dump_standard_cards_to_file(output_file)
