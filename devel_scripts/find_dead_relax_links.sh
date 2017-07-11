#! /bin/bash
###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

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
