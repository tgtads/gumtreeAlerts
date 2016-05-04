#!/usr/bin/bash

# this controlling script asks the gumtreeLatest.py crawler to
# ignore all featured items. It is fairly simple
# to enable this if desired

# recommended use
# cron > gumtreeTwitter.sh > gumtreeLatest.py > parseGumtreeAd.py > PTT

areas=("london" "manchester") ;

# the arguments to gumtreeLatest.py could be changed
# to cover categories other than housing..
categories=("flatshare-offered" "flats-and-houses-for-rent-offered") ;

# age in minutes
maxAge=30 ;

# your budget in £
maxPrice=150 ;

# useful for filtering out unwanted items
minPrice=60 ;

# the following is only useful if we're using parseGumtreeAd.py
# to look at particular areas of the ad
# Case-insensitive. Beware of partial string matches!
# forbidden character: §
keywords=("+washing machine" "-unfurnished") ;


rCount=0 ;
for area in ${areas[@]} ; do

    for category in ${categories[@]} ; do

        results=(`python3 gumtreeLatest.py -m $maxAge search_location=$area\&search_category=$category\&featured_filter=false\&min_price=$minPrice\&max_price=$maxPrice\&photos_filter=true`) ;

        for URL in ${results[@]} ; do

            kwsj=$(printf "§%s" "${keywords[@]}") ;
            allArgs=${kwsj:1}'§'$URL ;
            IFS=§ ;  # bash/escaped whitespace workaround
            isOK=`python3 parseGumtreeAd.py $allArgs` ;
            unset IFS ;

            if [ $isOK ] ; then

                rCount=$(($rCount+1)) ;
                shorterURL=`echo $URL | sed 's/^.*\//http:\/\/gumtree.com\/search?q=/'` ;
                text="Gumtree/"$area"/"$category": "$shorterURL ;

                if [ ${#text} -le 140 ] ; then
                    echo $text ;  # test mode
                    # twitter set $text ;  # requires configured command-line twitter client, ie. PTT
                fi ;

            fi ;

        done ;

    done ;

done ;

echo $rCount" valid items found." ;