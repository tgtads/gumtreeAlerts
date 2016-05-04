#!/usr/local/bin/python3

import argparse
import re
import urllib.request
from html.parser import HTMLParser

# HOW IT WORKS:

# The script is a search-term agnostic parser for the gumtree.com (UK)
# online classifieds site.

# It is designed to help users find the latest items while accepting all
# search terms (excepting those relating to age and sort order of course)
# that gumtree supports

# The optional flag is max age - the program stops processing pages and
# ignores any items that are older than maxage.

# Two features further increase functionality over the site itself:
# The ability to ignore featured items when featured_filter=False
# and to ignore irrelevant items outside of the search area

# USAGE EXAMPLES:

# python3 gumtreeLatest.py -m 59 'search_location=london
# &search_category=flatshare-offered&featured_filter=False
# &max_price=60&min_price=60'

# gumtreeLatest.py -m 59 'guess_search_category=phones&q=iphone+5s
# &search_category=phones&search_location=london&distance=0
# &min_price=&max_price=300'


# RETURN VALUES:

# relevant items are directly returned as a space-delimited list


def get_html(url):
    try:
        pageStream = urllib.request.urlopen(url)
        ph = pageStream.read()
        pageStream.close()
        try:
            phDecoded = ph.decode('utf-8')
#            phNocrlf = re.sub('\n', '', phDecoded)
            return phDecoded
        except UnicodeDecodeError as e:
            print(e, url)
    except urllib.request.URLError as e:
        print(e, url)


class MyHTMLParser(HTMLParser):
    rl = []

    def clear(self):
        self.rl = []

    def get(self):
        return self.rl


class PaginationLinksParser(MyHTMLParser):

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:  # for each tuple in list
                if attr[0] == 'href':
                    href = attr[1]
                if attr[0] == 'class' and attr[1] == 'page':
                    self.rl.append(href)


class ListedItemsParser(MyHTMLParser):  # this one helps ignore featured items

    def handle_starttag(self, tag, attrs):

        if tag == 'a':
            for attr in attrs:  # for each tuple in list
                if attr[0] == 'href':
                    self.rl.append(attr[1])  # extract link

        if (not FEATURED_FILTER) and tag == 'span':
            for attr in attrs:  # for each tuple in list
                if attr[0] == 'class' and attr[1] == 'ribbon-featured':
                    self.rl[-1] = 'IGNORE-FEATURED'  # overwrite

    def handle_data(self, data):

        t = re.compile('^\n([0-9]{1,}) (day|hour|min)s? ago\n$')
        if t.match(data):
            time = int(t.match(data).group(1))
            key = t.match(data).group(2)
            age = {'day':  (lambda: 60*24*time),
                   'hour': (lambda: 60*time),
                   'min':  (lambda: time)}[key]()
            if age > MAXAGE:
                self.rl.insert(-1, 'BRAKE-FOR-AGE')

        if data == ' miles outside of your search area\n':
            self.rl.append('BRAKE-FOR-IRRELEVANCE')


def unique(l):
    rl = []
    for i in l:
        if i not in rl:
            rl.append(i)
    return rl

# ------------------------ execution ----------------------

# parse given arguments -------------------

argparser = argparse.ArgumentParser()
argparser.add_argument("terms", type=str,
                       help=("Search fields and terms, ampersand separated. "
                             "Fields 'sort' and 'page' are ignored. "
                             "See http://www.gumtree.com/search? "
                             "for fields"))
argparser.add_argument("-m", "--maxage", type=int,
                       help="maximum age of items in minutes.")
args = argparser.parse_args()


if args.maxage:
    MAXAGE = int(args.maxage)
else:
    MAXAGE = 60*24*365*100  # good until 21xx :)


m = re.compile('featured_filter=true(&.*)?$',
               flags=re.IGNORECASE).match(args.terms)
if m:
    FEATURED_FILTER = True
else:
    FEATURED_FILTER = False


# clean the arguments for forbidden fields
OTHERFIELDS = re.sub('^&', '',
                     re.sub('(^|&)(sort|page)=[^&]*', '',
                            args.terms,
                            flags=re.IGNORECASE))

# download and parse pages -------------------

BASEURL = 'http://www.gumtree.com'
pageMax = 1
pageN = 1
flagged = False

adURLs = []

while not flagged:

    pageHTML = get_html(url=(BASEURL +
                             '/search' +
                             '?' + 'sort=date' +
                             '&' + 'page=' + str(pageN) +
                             '&' + OTHERFIELDS))

    parser = ListedItemsParser()
    parser.clear()
    parser.feed(pageHTML)

    for item in parser.get():
        if not flagged:
            m = re.compile('^/p/.*').match(item)
            if m:
                adURLs.append(BASEURL + m.group())
            if (item == 'BRAKE-FOR-AGE' or
                    item == 'BRAKE-FOR-IRRELEVANCE'):
                flagged = True

    # get pagination links from the first page
    if pageN == 1:

        parser = PaginationLinksParser()
        parser.clear()
        parser.feed(pageHTML)

        # find biggest number of pages referenced in the links
        for item in parser.get():
            m = re.search('/page([0-9]{1,})\?', item)
            if m and int(m.group(1)) > pageMax:
                pageMax = int(m.group(1))

    if pageN >= pageMax:
        flagged = True
    else:
        pageN += 1


# return results, if any -------------------

print(' '.join(unique(adURLs)))
