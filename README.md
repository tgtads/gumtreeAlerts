gumtreeAlerts:

This suite of tools is written in Python 3 and requires urllib and html.parser.

The python scripts are simple html parsers, with gumtree-specific logic,
that can be called independently from the command line.

github.com/tgtads
thomas.geraint.adams@gmail.com


gumtreeTwitter.sh:

This is an example of a controlling script that shows how the python scripts
work together, and calls PTT (python twitter tools) to notify the user of any
relevant items posted to gumtree.

I prefer to execute the script from cron every 30 minutes.


gumtreeLatest.py:

The gumtreeLatest.py script is a parser for the gumtree.com (UK)
online classifieds site. Specifically, it parses the resulting list of
article previews.

Relevant items are directly returned as a space-delimited list.

With the optional maxage flag, the program stops processing pages and
ignores any items that are older than maxage.

Two features further increase functionality over the site itself:
The ability to ignore featured items when featured_filter=False
and to ignore irrelevant items that are outside of the scope of the search

Example:
python3 gumtreeLatest.py -m 59 'search_location=london
&search_category=flatshare-offered&featured_filter=False
&max_price=60&min_price=60'


parseGumtreeAd.py:

The parseGumtreeAd script is a parser for individual classified articles.
It obtains the item as defined by URL and parses the data fields for
keywords as defined from +'includes' and -'excludes' in the arguments.
Acceptance or rejection of the item is returned.

Example:
python3 parseAd.py -stunning +'nice place' -terrible\ place url




