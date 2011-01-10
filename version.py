###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for relax version information."""

# Python module imports.
from os import F_OK, access
from string import split
from subprocess import PIPE, Popen


version = "1.3.7"


def get_revision():
    """Attempt to retrieve the SVN revision number, if this is a checked out copy.

    @return:    The SVN revision number, or None if unsuccessful.
    @rtype:     None or str
    """

    # Does the base directory exist (i.e. is this a checked out copy).
    if not access('.svn', F_OK):
        return

    # Try to run 'svn info'.
    pipe = Popen('svn info', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)

    # Errors.
    if pipe.stderr.readlines():
        return

    # Loop over the output lines.
    for line in pipe.stdout.readlines():
        # Split up the line.
        row = split(line)

        # The revision.
        if row[0] == 'Revision:':
            return row[1]


def get_url():
    """Attempt to retrieve the SVN URL, if this is a checked out copy.

    @return:    The SVN URL, or None if unsuccessful.
    @rtype:     None or str
    """

    # Does the base directory exist (i.e. is this a checked out copy).
    if not access('.svn', F_OK):
        return

    # Try to run 'svn info'.
    pipe = Popen('svn info', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)

    # Errors.
    if pipe.stderr.readlines():
        return

    # Loop over the output lines.
    for line in pipe.stdout.readlines():
        # Split up the line.
        row = split(line)

        # The revision.
        if row[0] == 'URL:':
            return row[1]
