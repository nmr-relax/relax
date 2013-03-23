###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Module for the statistical concept of model selection."""

# Python module imports.
from math import log

# relax module imports.
from lib.errors import RelaxError


def aic(chi2, k, n):
    """Akaike's Information Criteria (AIC).

    The formula is::

        AIC = chi2 + 2k


    @param chi2:    The minimised chi-squared value.
    @type chi2:     float
    @param k:       The number of parameters in the model.
    @type k:        int
    @param n:       The dimension of the relaxation data set.
    @type n:        int
    @return:        The AIC value.
    @rtype:         float
    """

    return chi2 + 2.0*k


def aicc(chi2, k, n):
    """Small sample size corrected AIC.

    The formula is::

                           2k(k + 1)
        AICc = chi2 + 2k + ---------
                           n - k - 1


    @param chi2:    The minimised chi-squared value.
    @type chi2:     float
    @param k:       The number of parameters in the model.
    @type k:        int
    @param n:       The dimension of the relaxation data set.
    @type n:        int
    @return:        The AIC value.
    @rtype:         float
    """

    if n > (k+1):
        return chi2 + 2.0*k + 2.0*k*(k + 1.0) / (n - k - 1.0)
    elif n == (k+1):
        raise RelaxError("The size of the dataset, n=%s, is too small for this model of size k=%s.  This situation causes a fatal division by zero as:\n    AICc = chi2 + 2k + 2k*(k + 1) / (n - k - 1).\n\nPlease use AIC model selection instead." % (n, k))
    elif n < (k+1):
        raise RelaxError("The size of the dataset, n=%s, is too small for this model of size k=%s.  This situation produces a negative, and hence nonsense, AICc score as:\n    AICc = chi2 + 2k + 2k*(k + 1) / (n - k - 1).\n\nPlease use AIC model selection instead." % (n, k))


def bic(chi2, k, n):
    """Bayesian or Schwarz Information Criteria.

    The formula is::

        BIC = chi2 + k ln n


    @param chi2:    The minimised chi-squared value.
    @type chi2:     float
    @param k:       The number of parameters in the model.
    @type k:        int
    @param n:       The dimension of the relaxation data set.
    @type n:        int
    @return:        The AIC value.
    @rtype:         float
    """

    return chi2 + k * log(n)
