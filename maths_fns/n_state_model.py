###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
from numpy import float64, zeros

# relax module imports.
from chi2 import chi2


class N_state_opt:
    """Class containing the target function of the optimisation of the N-state model."""

    def __init__(self, N=None, init_params=None, full_tensors=None, red_data=None, red_errors=None):
        """Set up the class instance for optimisation.

        All constant data required for the N-state model are initialised here.


        @param N:               The number of states.
        @type N:                int
        @param init_params:     The initial parameter values.  Optimisation must start at some
                                point!
        @type init_params:      numpy float64 array
        @param full_tensors:    A list of the full alignment tensors in matrix form.
        @type full_tensors:     list of 3x3 numpy matricies
        @param red_data:        An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced
                                tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2, Syy2,
                                Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn]
        @type red_data:         numpy float64 array
        @param red_errors:      An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced
                                tensors.  The array format is the same as for red_data.
        @type red_errors:       numpy float64 array
        """

        # Store the data inside the class instance namespace.
        self.N = N
        self.params = 1.0 * init_params    # Force a copy of the data to be stored.
        self.total_num_params = len(init_params)
        self.full_tensors = full_tensors
        self.red_data = red_data
        self.red_errors = red_errors

        # Initialise some empty matrices for storage of the transient rotation matricies and their transposes.
        self.R = []
        self.RT = []
        for i in xrange(N):
            self.R.append(zeros((3,3), float64))
            self.RT.append(zeros((3,3), float64))


    def func(self, params):
        """The target function for optimisation.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the single chi-squared value
        corresponding to that coordinate in the parameter space.  If no tensor errors are supplied,
        then the SSE (the sum of squares error) value is returned instead.  The chi-squared is
        simply the SSE normalised to unit variance (the SS divided by the error squared).

        @param params:  The vector of parameter values.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @type return:   float
        """

        # Return the chi-squared value.
        return chi2(self.red_data, red_bc_data, self.red_errors)
