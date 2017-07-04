#! /bin/sh
###############################################################################
#                                                                             #
# Copyright (C) 2017 Edward d'Auvergne                                        #
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


export SVN_REPO="/data/relax/gna/repository_backup/git_migration/svn_cleanup"
export BASE_DIR="/data/relax/gna/repository_backup/git_migration/gitsvn_manual"
cd $BASE_DIR
rm -rf repo

# Repo init.
git init repo
cd repo
touch .gitignore
git add .gitignore
git commit -m "Created an empty .gitignore to initialise the repository."

# SVN to git authors.
git config --add svn.authorsfile ../../authors-transform.txt

# Trunk branches.
for TRUNK in 0.1 0.2 0.3 1.0 1.1 1.2 1.3
do
    git config --add svn-remote.$TRUNK.noMetadata 1
    git config --add svn-remote.$TRUNK.url file://$SVN_REPO/$TRUNK
    git config --add svn-remote.$TRUNK.fetch :refs/remotes/origin/$TRUNK\_svn
done

# Main layout.
git svn init file://$SVN_REPO/ --no-metadata --stdlayout

# Conversion.
git svn fetch --fetch-all 2>&1 | tee $BASE_DIR/fetch.log
