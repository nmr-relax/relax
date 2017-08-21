###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Script for numerically calculating the exponential curve gradient."""

# Python module imports.
from math import exp
from numpy import array
from numdifftools import Jacobian


def func(params):
    """Calculate the chi-squared value."""

    global times, I, errors

    # Unpack the parameters.
    R, I0 = params

    # The intensities.
    back_calc = []
    for i in range(len(times)):
        back_calc.append(I0 * exp(-R*times[i]))

    # The chi2 elements.
    chi2 = []
    for i in range(len(times)):
        chi2.append((I[i] - back_calc[i])**2 / errors[i]**2)

    # Return the value.
    return array(chi2)


# The real parameters.
R = 1.0
I0 = 1000.0

# The time points.
times = [0.0, 1.0, 2.0, 3.0, 4.0]

# The intensities for the above I0 and R.
I = [1000.0, 367.879441171, 135.335283237, 49.7870683679, 18.3156388887]

# The intensity errors.
errors = [10.0, 10.0, 10.0, 10.0, 10.0]

# Set up the Jacobian function.
jacobian = Jacobian(func)

# The numeric Jacobian at the minimum.
print("\n\nOn-minimum:\n")
matrix = jacobian([R, I0])
print("The Chi2 Jacobian at %s is:\n%s" % ([R, I0], matrix))

# The numeric Jacobian off the minimum.
print("\n\nOff-minimum:\n")
R = 2.0
I0 = 500.0
matrix = jacobian([R, I0])
print("The Chi2 Jacobian at %s is:\n%s" % ([R, I0], matrix))
