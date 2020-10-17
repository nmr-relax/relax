#!/bin/bash
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

# Back up script for retrieving the MediaWiki files for the relax wiki.

# Variables.
BACKUP_FOLDER="/data/relax/wiki/filedump"
MYDATE=`date '+%Y%m%d_%H%M'`
MYTIME=`date '+%Y-%m-%d %T'`
SF_USERNAME="USERNAME"
BACKUP_FOLDER_MIRROR="${BACKUP_FOLDER}/mirror"
BACKUP_FOLDER_CURRENT="${BACKUP_FOLDER}/current"

# Logging
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>>${BACKUP_FOLDER}/filedump.log 2>&1

# Make sure everything worked.
exec_test() {
    if [ $? -ne 0 ]; then
       printf -- "Command failed, exiting script.\n\n"
       exit 1;
    fi
}

dump_base() {
    printf -- "#######################################\n"
    printf -- "Starting file sync, $MYTIME\n"
    printf -- "Mirror syncing...\n"
    CMD="rsync -av --delete -e ssh $SF_USERNAME@web.sourceforge.net:/home/project-web/nmr-relax/htdocs/wiki/ $BACKUP_FOLDER_MIRROR"
    printf -- "$CMD\n"
    eval "$CMD"
}

compress_base() {
    printf -- "Compressing current...\n"
    DIFF=`diff -q -r $BACKUP_FOLDER_MIRROR $BACKUP_FOLDER_CURRENT`
    printf -- "Difference between sync and current is: %s\n" "$DIFF"
    DIFFARR=($DIFF)
    LENDIFFARR=${#DIFFARR[@]}
    if [ "$LENDIFFARR" -gt "0" ]
    then
        rm -rf $BACKUP_FOLDER_CURRENT
        cp -p -r $BACKUP_FOLDER_MIRROR $BACKUP_FOLDER_CURRENT
        tar -zcf ${BACKUP_FOLDER}/filedump_${MYDATE}.tar.gz $BACKUP_FOLDER_CURRENT/
    fi
}

# The file backup.
mkdir -p $BACKUP_FOLDER $BACKUP_FOLDER_MIRROR $BACKUP_FOLDER_CURRENT
dump_base; exec_test
compress_base; exec_test
printf -- "Finished synchronisation.\n\n"
