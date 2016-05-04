#!/usr/local/bin/python3

import re
import urllib.request
from html.parser import HTMLParser
import sys

# how this works:
# this loads the item from the given the URL and parses the data fields for
# keywords as defined from +'includes' and -'excludes' in the arguments
# acceptance or rejection of the item is returned

# usage example:
# python3 parseAd.py -stunning +'nice place' -terrible\ place url


def get_html(url):
    try:
        pageStream = urllib.request.urlopen(url)
        ph = pageStream.read()
        pageStream.close()
        try:
            phDecoded = ph.decode('utf-8')
            phNocrlf = re.sub('\n', '', phDecoded)
            return phNocrlf
        except UnicodeDecodeError as e:
            print(e, "for", url)
    except urllib.request.URLError as e:
        print(e, "for", url)


class Tag(object):
    name = ""
    attrs = []

    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs


class MatchingHTMLParser(HTMLParser):
    rs = ""
    flag = False

    # sadly we can't create a custom init
    # as this would replace the parent

    def clear(self):
        self.rs = ""
        self.flag = False

    def get(self):
        return self.rs

    def handle_starttag(self, tag, attrs):
        if tag == self.t.name and attrs == self.t.attrs:
            self.flag = True  # found the rel opening tag

    def handle_data(self, data):
        if self.flag:
            self.rs += data + '\n'  # get any data within that tag

    def handle_endtag(self, tag):
        if tag == self.t.name:
            self.flag = False  # until tag is closed


class h1Parser(MatchingHTMLParser):
    t = Tag('h1', [('itemprop', 'name'), ('class', 'space-mbs')])


class dl1Parser(MatchingHTMLParser):
    t = Tag('dl', [('class', 'dl-attribute-list attribute-list1')])


class dl2Parser(MatchingHTMLParser):
    t = Tag('dl', [('class', 'dl-attribute-list attribute-list2')])


class pParser(MatchingHTMLParser):
    t = Tag('p', [('class', 'ad-description'), ('itemprop', 'description')])


def feed_parser(text, parser):
    p = parser
    p.clear()
    p.feed(text)
    return(p.get())


# parsing arguments:

url = str(sys.argv[-1])

keywords = sys.argv[1:-1]

includes = []
excludes = []
for k in keywords:
    if k[0] == '+':
        includes.append(k.lstrip('+'))
    if k[0] == '-':
        excludes.append(k.lstrip('-'))


if (len(includes)+len(excludes)) < 1:

    print("script error, 0 keyword arguments found")

else:

    pageHTML = get_html(url)

    if isinstance(pageHTML, str):
        if len(pageHTML) > 0:
            # obtaining the inner data

            header = feed_parser(text=pageHTML, parser=h1Parser())
            summary1 = feed_parser(text=pageHTML, parser=dl1Parser())
            summary2 = feed_parser(text=pageHTML, parser=dl2Parser())
            description = feed_parser(text=pageHTML, parser=pParser())

            # checking returned texts for keywords

            toSearch = (header + " " +
                        summary1 + " " +
                        summary2 + " " +
                        description)

            keepAd = True

            for i in includes:
                matchedIncluded = re.search(i, toSearch, flags=re.IGNORECASE)
                if not matchedIncluded:
                    keepAd = False

            for i in excludes:
                matchedExcluded = re.search(i, toSearch, flags=re.IGNORECASE)
                if matchedExcluded:
                    keepAd = False

            if keepAd:
                print("Accepted")
            else:
                print(url, "Rejected")
