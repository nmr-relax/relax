#!/bin/bash
# -*- coding: UTF-8 -*-
# Script for dumping ftp server automatically using cron.
#
# This script was taken from the post Troels Linnet at: http://article.gmane.org/gmane.science.nmr.relax.devel/4168.

# exec test
exec_test () {
[ $? -eq 0 ] && echo "-- Command successfully executed" || echo "-- Command failed; exit 1"
}

# Filenames
dbhost="web3.gigahost.dk"
# The following two fields are kept secret, to prevent abuse.
# Please contact Troels Linnet at: tlinnet _at_ gmail dot com, for access.
dbuser="secret"
dbpwd="secret"

mydate=`date '+%Y%m%d_%H%M'`
mytime=`date '+%T %Y%m%d'`
backupfolder="${HOME}/backup/ftpdump"
backupfoldermirror="${backupfolder}/mirror"
backupfoldercurrent="${backupfolder}/current"
mkdir -p $backupfolder $backupfoldermirror $backupfoldercurrent

# Logging
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>${backupfolder}/ftpdump.log 2>&1
# Everything below will go to the log file

dump_base () {
echo "###########################"
echo "STARTING on: $mytime"
echo "Mirror syncing..."
cd $backupfoldermirror
lftp -e "open ftp://${dbuser}:${dbpwd}@${dbhost} && mirror --no-perms --exclude-glob backup_scripts/ --exclude-glob cache/ --exclude-glob LocalSettings.php --parallel=10 && bye"
}

compress_base () {
echo "Compressing current..."
DIFF=`diff -q -r $backupfoldermirror $backupfoldercurrent`
echo -e "Difference between sync and current is:\n$DIFF"
DIFFARR=($DIFF)
LENDIFFARR=${#DIFFARR[@]}
if [ "$LENDIFFARR" -gt "0" ]
then
rm -rf $backupfoldercurrent
cp -p -r $backupfoldermirror $backupfoldercurrent
tar -zcf ${backupfolder}/ftpdump_${mydate}.tar.gz $backupfoldercurrent/
fi
}

dump_base ; exec_test
compress_base ; exec_test

echo "Done, quit!"
