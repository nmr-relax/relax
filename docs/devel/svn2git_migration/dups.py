#! /usr/bin/env python3
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

# Python module imports.
from os import chdir
from subprocess import PIPE, Popen


# The repository.
REPO = "/data/relax/gna/repository_backup/git_migration/gitsvn_manual/repo_trunk_fix"


def get_hashes():
    """Get all the git hashes and first commit lines for the repository."""

    # Init.
    hashes = {}

    # Exec.
    pipe = Popen("git log --all --pretty=format:'%H xxxxxxxxxx %s %an (%cd)' --date=iso", shell=True, stdout=PIPE, close_fds=False)

    # Get the data.
    for line in pipe.stdout.readlines():
        # Split up the line.
        hash, msg = line.decode().split(' xxxxxxxxxx ')
        msg = msg[:-1]

        # Store the data.
        if msg not in hashes:
            hashes[msg] = [hash]
        else:
            hashes[msg].append(hash)

    # Return the data structure.
    return hashes


# Get the hashes.
chdir(REPO)
hashes = get_hashes()

# Checks.
for msg in hashes:
    if len(hashes[msg]) >= 2:
        print("Hashes replicated for \"%s\" (%s)." % (msg, hashes[msg]))
