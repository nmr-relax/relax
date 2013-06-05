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
"""Module for calculating simple statistics."""

# Python module imports.
from math import exp, pi, sqrt


def bucket(values=None, lower=0.0, upper=200.0, inc=100, verbose=False):
    """Generate a discrete probability distribution for the given values.

    @keyword values:    The list of values to convert.
    @type values:       list of float
    @keyword lower:     The lower bound of the distribution.
    @type lower:        float
    @keyword upper:     The upper bound of the distribution.
    @type upper:        float
    @keyword inc:       The number of discrete increments for the distribution between the lower and upper bounds.
    @type inc:          int
    @keyword verbose:   A flag which if True will enable printouts.
    @type verbose:      bool
    @return:            The discrete probability distribution.
    @rtype:             list of lists of float
    """

    # The bin width.
    bin_width = (upper - lower)/float(inc)

    # Init the dist object.
    dist = []
    for i in range(inc):
        dist.append([bin_width*i+lower, 0])

    # Loop over the values.
    for val in values:
        # The bin.
        bin = int((val - lower)/bin_width)

        # Outside of the limits.
        if bin < 0 or bin >= inc:
            if verbose:
                print("Outside of the limits: '%s'" % val)
            continue

        # Increment the count.
        dist[bin][1] = dist[bin][1] + 1

    # Convert the counts to frequencies.
    total_pr = 0.0
    for i in range(inc):
        dist[i][1] = dist[i][1] / float(len(values))
        total_pr = total_pr + dist[i][1]

    # Printout.
    if verbose:
        print("Total Pr: %s" % total_pr)

    # Return the dist.
    return dist


def gaussian(x=None, mu=0.0, sigma=1.0):
    """Calculate the probability for a Gaussian probability distribution for a given x value.

    @keyword x:     The x value to calculate the probability for.
    @type x:        float
    @keyword mu:    The mean of the distribution.
    @type mu:       float
    @keyword sigma: The standard deviation of the distribution.
    @type sigma:    float
    @return:        The probability corresponding to x.
    @rtype:         float
    """

    # Calculate and return the probability.
    return exp(-(x-mu)**2 / (2.0*sigma**2)) / (sigma * sqrt(2.0 * pi))


def std(values=None, skip=None, dof=1):
    """Calculate the standard deviation of the given values, skipping values if asked.

    @keyword values:    The list of values to calculate the standard deviation of.
    @type values:       list of float
    @keyword skip:      An optional list of booleans specifying if a value should be skipped.  The length of this list must match the values.  An element of True will cause the corresponding value to not be included in the calculation.
    @type skip:         list of bool or None.
    @keyword dof:       The degrees of freedom, whereby the standard deviation is multipled by 1/(N - dof).
    @type dof:          int
    @return:            The standard deviation.
    @rtype:             float
    """

    # The total number of points.
    n = 0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Increment n.
        n = n + 1

    # Calculate the sum of the values for all points.
    Xsum = 0.0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Sum.
        Xsum = Xsum + values[i]

    # Calculate the mean value for all points.
    if n == 0:
        Xav = 0.0
    else:
        Xav = Xsum / float(n)

    # Calculate the sum part of the standard deviation.
    sd = 0.0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Sum.
        sd = sd + (values[i] - Xav)**2

    # Calculate the standard deviation.
    if n <= 1:
        sd = 0.0
    else:
        sd = sqrt(sd / (float(n) - float(dof)))

    # Return the SD.
    return sd
