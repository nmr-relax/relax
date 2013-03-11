###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module for relax version information."""

# Dependencies.
import dep_check

# Python module imports.
from os import F_OK, access, sep
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen

# relax module imports.
from status import Status; status = Status()


version = "repository checkout"


def revision():
    """Attempt to retrieve the SVN revision number, if this is a checked out copy.

    @return:    The SVN revision number, or None if unsuccessful.
    @rtype:     None or str
    """

    # Does the base directory exist (i.e. is this a checked out copy).
    if not access(status.install_path+sep+'.svn', F_OK):
        return

    # Python 2.3 and earlier.
    if Popen == None:
        return

    # Try to run 'svn info'.
    pipe = Popen('svn info %s' % status.install_path, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Errors.
    if pipe.stderr.readlines():
        return

    # Loop over the output lines.
    for line in pipe.stdout.readlines():
        # Split up the line.
        row = line.split()

        # The revision.
        if len(row) and row[0] == 'Revision:':
            return row[1]


def url():
    """Attempt to retrieve the SVN URL, if this is a checked out copy.

    @return:    The SVN URL, or None if unsuccessful.
    @rtype:     None or str
    """

    # Does the base directory exist (i.e. is this a checked out copy).
    if not access(status.install_path+sep+'.svn', F_OK):
        return

    # Python 2.3 and earlier.
    if Popen == None:
        return

    # Try to run 'svn info'.
    pipe = Popen('svn info %s' % status.install_path, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Errors.
    if pipe.stderr.readlines():
        return

    # Loop over the output lines.
    for line in pipe.stdout.readlines():
        # Split up the line.
        row = line.split()

        # The revision.
        if len(row) and row[0] == 'URL:':
            return row[1]


def version_full():
    """Return the full relax version, including all SVN info for repository versions.

    @return:    The relax version string.
    @rtype:     str
    """

    # The relax version.
    ver = version

    # Repository version.
    if ver == 'repository checkout':
        # Get the SVN revision and URL.
        svn_rev = revision()
        svn_url = url()

        # Change the version string.
        if svn_rev:
            ver = version + " r" + svn_rev
        if svn_url:
            ver = ver + " " + svn_url

    # Return the version.
    return ver
