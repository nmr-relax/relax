#! /bin/bash
# -*- coding: UTF-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2013 Troels E. Linnet                                         #
# Copyright (C) 2020 Edward d'Auvergne                                        #
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

# Back up script for the MySQL database behind the relax wiki.

# Variables.
BACKUP_FOLDER="/data/relax/wiki/mysqldump"
DBHOST="mysql-n"
# The following three fields are kept secret, to prevent abuse. 
# Please contact Edward d'Auvergne at: edward _at_ nmr-relax dot com, for access.
DATABASE=""
DBUSER=""
DBPASSWD=""
MYDATE=`date '+%Y%m%d_%H%M'`
MYTIME=`date '+%Y-%m-%d %T'`
SF_USERNAME="USERNAME"
FILENAME1="${DATABASE}_${MYDATE}.sql.gz"
FILENAME2="${DATABASE}_${MYDATE}.xml.gz"
FILENAME3="${DATABASE}*.gz"

# Logging
exec 3>&1 4>&2
#trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>${BACKUP_FOLDER}/${DATABASE}.log 2>&1

# Make sure everything worked.
exec_test() {
    if [ $? -ne 0 ]; then
       printf -- "Command failed, exiting script.\n\n"
       exit 1;
    fi
}

# Try the command few times, in case of a "Connection closed by 216.105.38.24 port 22" SF error.
looping_sf_exec() {
    CMD="ssh -t $SF_USERNAME@shell.sourceforge.net '$1'"
    echo $CMD; eval $CMD
    while [ $? -ne 0 ] || (( count++ >= 5 )); do
        echo $CMD; eval $CMD
    done
}

# Initial printout.
printf -- "\n#################################################\n"
printf -- "Starting remote MySQL backup, $MYTIME\n"

# First initialise the Shell Service, if necessary.
printf -- "Opening the Shell Service...\n"
CMD="ssh $SF_USERNAME@shell.sourceforge.net create"
echo $CMD; eval $CMD
while [ $? -ne 0 ] || (( count++ >= 5 )); do
    echo $CMD; eval $CMD
done
exec_test

# The remote MySQL backup.
printf -- "Remote base dumping...\n"
looping_sf_exec "mysqldump --opt --host=$DBHOST --user=$DBUSER --password=$DBPASSWD $DATABASE | gzip -f9 > $FILENAME1"; exec_test
printf -- "Remote XML dumping...\n"
looping_sf_exec "mysqldump --opt --host=$DBHOST --user=$DBUSER --password=$DBPASSWD $DATABASE --xml | gzip -f9 > $FILENAME2"; exec_test
printf -- "Finished remote MySQL backup.\n\n"

# Fetch the files.
printf -- "Copying backup files.\n"
mkdir -p $BACKUP_FOLDER
CMD="rsync -av -e ssh $SF_USERNAME@frs.sourceforge.net:$FILENAME1 $BACKUP_FOLDER"
echo $CMD; eval $CMD
CMD="rsync -av -e ssh $SF_USERNAME@frs.sourceforge.net:$FILENAME2 $BACKUP_FOLDER"
echo $CMD; eval $CMD
printf -- "Finished copying.\n\n"

# Remove the remote files.
printf -- "Deleting remote backup files.\n"
looping_sf_exec "rm -f $FILENAME3"; exec_test
printf -- "Finished deleting.\n\n"
