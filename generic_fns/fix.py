###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2008 Edward d'Auvergne                        #
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
"""Module for holding certain model components fixed during optimisation."""

# Python module imports.
from re import match

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError





class Fix:
    def __init__(self, relax):
        """Class containing the function for fixing or allowing parameter values to change."""

        self.relax = relax


    def fix(self, run, element, fixed):
        """Function for fixing or allowing parameter values to change."""

        # Test if the run exists.
        if not run in ds.run_names:
            raise RelaxNoPipeError, run

        # Diffusion tensor.
        if element == 'diff':
            # Test if the diffusion tensor data is loaded.
            if not ds.diff.has_key(run):
                raise RelaxNoTensorError, 'diffusion'

            # Set the fixed flag.
            ds.diff[run].fixed = fixed


        # All residues.
        elif element == 'all_res':
            # Test if sequence data is loaded.
            if not ds.res.has_key(run):
                raise RelaxNoSequenceError, run

            # Loop over the sequence and set the fixed flag.
            for i in xrange(len(ds.res[run])):
                ds.res[run][i].fixed = fixed


        # All parameters.
        elif element == 'all':
            # Test if sequence data is loaded.
            if not ds.res.has_key(run):
                raise RelaxNoSequenceError, run

            # Test if the diffusion tensor data is loaded.
            if not ds.diff.has_key(run):
                raise RelaxNoTensorError, 'diffusion'

            # Set the fixed flag for the diffusion tensor.
            ds.diff[run].fixed = fixed

            # Loop over the sequence and set the fixed flag.
            for i in xrange(len(ds.res[run])):
                ds.res[run][i].fixed = fixed


        # Unknown.
        else:
            raise RelaxError, "The 'element' argument " + `element` + " is unknown."
