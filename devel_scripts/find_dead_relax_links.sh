#! /bin/bash

# Script for extracting all http://www.nmr-relax.com URLs within all text files in a directory tree, and then determining which links are dead.

while read line
do
    if ! curl --output /dev/null --silent --head --fail $line; then
        echo "$line"
    fi
done < <(grep -r http . \
| sed "s/http/\nhttp/g" \
| grep "http://www.nmr-relax" \
| sed "s/\">.*//g" \
| sed "s/<\/.>.*//g" \
| sed "s/\" .*//g" \
| sed "s/&quot.*//g" \
| sed "s/;\/.*//g" \
| sed "s/}.*//g" \
| sed "s/ .*//g" \
| sed "s/\\\\_/_/g" \
| sed "s/\".*//g" \
| sed "s/<br>.*//g" \
| sed "s/<u>.*//g" \
| sed "s/,$//g" \
| sed "s/#.*//g" \
| sed "s/).*//g" \
| sed "s/\%s.*//g" \
| sed "s/\.$//g" \
| sed "s/&gt.*//g" \
| sed "s/'.*//g" \
| sed "s/>.*//g" \
| sed "s/\/>.*//g" \
| sed "s/<\/tt.*//g" \
| sort -u)
