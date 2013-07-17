#!/bin/bash
# -*- coding: UTF-8 -*-
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
