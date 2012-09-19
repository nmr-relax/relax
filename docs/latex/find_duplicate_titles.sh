#! /bin/sh

grep "section{" *.tex -h \
| grep -v subsubsection \
| sed "s/subsection//g" \
| sed "s/section//g" \
| sed "s/    //g" \
| sed "s/ \\\\label.*//g" \
| sed "s/{//g" \
| sed "s/}//g" \
| sed "s/^\\\\//g" \
| sed "s/^The //g" \
| sed "s/\\\\-//g" \
| sed "s/\\\\//g" \
| tr '[:upper:]' '[:lower:]' \
| sort \
| uniq -cd
