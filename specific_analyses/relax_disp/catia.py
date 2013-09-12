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
"""Functions for interfacing with Flemming Hansen's CATIA program."""

# relax module imports.
from lib.io import mkdir_nofail
from pipe_control import pipes
from pipe_control.mol_res_spin import check_mol_res_spin_data
from specific_analyses.relax_disp.checks import check_model_type, check_spectra_id_setup


def catia_input(file='Fit.catia', dir=None, force=False):
    """Create the CATIA input files.

    @keyword file:      The main CATIA execution file.
    @type file:         str
    @keyword dir:       The optional directory to place the files into.  If None, then the files will be placed into the current directory.
    @type dir:          str or None
    @keyword force:     A flag which if True will cause all pre-existing files to be overwritten.
    @type force:        bool
    """

    # Data checks.
    pipes.test()
    check_mol_res_spin_data()
    check_spectra_id_setup()
    check_model_type()

    # Directory creation.
    if dir != None:
        mkdir_nofail(dir, verbosity=0)
