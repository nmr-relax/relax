#!/bin/bash
# -*- coding: UTF-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2013 Troels E. Linnet                                         #
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

# Script for dumping MySQL base automatically using cron.
#
# This script was taken from the post Troels Linnet at: http://article.gmane.org/gmane.science.nmr.relax.devel/4163.

# exec test
exec_test () {
[ $? -eq 0 ] && echo "-- Command successfully executed" || echo "-- Command failed; exit 1"
}

# Filenames
dbhost="mysql13.gigahost.dk"
# The following three fields are kept secret, to prevent abuse. 
# Please contact Troels Linnet at: tlinnet _at_ gmail dot com, for access.
dbuser="secret"
dbpwd="secret"
dbname="secret_nmrrelax"
backupfolder="$HOME/backup/mysqldump"
mkdir -p $backupfolder
mydate=`date '+%Y%m%d_%H%M'`
mytime=`date '+%T %Y%m%d'`
filename1="${backupfolder}/${dbname}_${mydate}.bck.sql"

# Logging
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>${backupfolder}/${dbname}.log 2>&1
# Everything below will go to the log file

dump_base () {
    echo "###########################"
    echo "STARTING on: $mytime"
    echo "Base dumping..."
    mysqldump --opt --host=$dbhost --user=$dbuser --password=$dbpwd $dbname > $filename1
}

compress_base () {
	echo "Compressing base..."
    gzip -f9 $filename1
    # rm filename1
}

dump_base ; exec_test
compress_base ; exec_test

echo "Done, quit!"
