###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module for handling result files."""

# relax module imports.
from status import Status; status = Status()


def add_result_file(type=None, label=None, file=None):
    """Add a results file to the current data pipe.

    @keyword type:  The mimetype of the result file, for example 'text', 'grace', 'molmol' or 'pymol'.
    @type type:     str
    @keyword label: The label to attach to the file.  For example a BMRB file can have the label 'BMRB' and type 'text'.
    @type label:    str
    @keyword file:  The path of the file.
    @type file:     str
    """

    # First check if the structure exists, creating it if needed.
    if not hasattr(cdp, 'result_files'):
        cdp.result_files = []

    # Check if the file already exists.
    for i in range(len(cdp.result_files)): 
        if cdp.result_files[i][2] == file:
            # Overwrite the settings.
            cdp.result_files[i][0] = type
            cdp.result_files[i][1] = label

            # Nothing left to do.
            return True

    # Add the file.
    cdp.result_files.append([type, label, file])

    # Notify all observers.
    status.observers.result_file.notify()
