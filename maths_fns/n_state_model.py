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


class N_state_model:
    """Class containing the target function of the optimisation of the N-state model."""

    def __init__(self):
        """Set up the class instance for optimisation.

        All constant data required for the N-state model should be initialised here.
        """


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
