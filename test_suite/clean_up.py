###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module of functions for cleaning up after the tests."""

# Python module imports.
from shutil import rmtree
from time import sleep

# relax module imports.
from compat import builtins
from lib.io import delete


def deletion(obj=None, name=None, dir=False):
    """Cleanly removing files and directories, handling WindowsErrors.

    The problem of MS Windows not releasing the file handle on a close() call is handled.  This method should be resilient to the strange MS Windows behaviour of not releasing the relax state files.  It should complete even when this WindowsError occurs.  A delay of 3 seconds has been added when the WindowsError occurs to give the OS some time before attempting to delete the directory or file again.  If this fails the deletion operation is skipped.


    @keyword obj:   The base object containing the file or directory name variable.
    @type obj:      Python object
    @keyword name:  The name of the file or directory name variable.
    @type name:     str
    @keyword dir:   A flag which if True indicates that a directory should be removed.  Otherwise a file should be deleted.
    """

    # No variable present.
    if not hasattr(obj, name):
        return

    # The variable.
    var = getattr(obj, name)

    # Non-windows systems.
    if not hasattr(builtins, 'WindowsError'):
        builtins.WindowsError = None

    # Attempt to remove the file or directory as well as the variable.
    try:
        if dir:
            rmtree(var)
        else:
            delete(var, fail=False)
        del var

    # Handle MS Windows strangeness.
    except WindowsError:
        sleep(3)
        try:
            if dir:
                rmtree(var)
            else:
                delete(var, fail=False)
        finally:
            del var
