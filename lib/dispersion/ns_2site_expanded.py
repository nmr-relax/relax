###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Paul Schanda (https://gna.org/users/pasa)           #
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
# but WITHOUT ANY WARRANTY without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""This function performs a numerical fit of 2-site Bloch-McConnell equations for CPMG-type experiments.

This function is exact, just as the explicit Bloch-McConnell numerical treatments.  It comes from a Maple derivation based on the Bloch-McConnell equations.  It is much faster than the numerical Bloch-McConnell solution.  It was derived by Nikolai Skrynnikov and is provided with his permission.

The code originates as optimization function number 5 from the fitting_main_kex.py script from Mathilde Lescanne, Paul Schanda, and Dominique Marion (see http://thread.gmane.org/gmane.science.nmr.relax.devel/4138, https://gna.org/task/?7712#comment2 and https://gna.org/support/download.php?file_id=18262).
"""

# Dependency check module.
import dep_check

# Python module imports.
from math import log
import numpy
from numpy import add, complex, conj, dot, exp, power, real
from numpy.linalg import matrix_power
if dep_check.scipy_module:
    from scipy.linalg import expm


def r2eff_ns_2site_expanded(r20=None, pA=None, dw=None, k_AB=None, k_BA=None, relax_time=None, inv_relax_time=None, tcp=None, back_calc=None, num_points=None, num_cpmg=None):
    """The 2-site numerical solution to the Bloch-McConnell equation using complex conjugate matrices.

    This function calculates and stores the R2eff values.


    @keyword r20:               The R2 value for both states A and B in the absence of exchange.
    @type r20:                  float
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword dw:                The chemical exchange difference between states A and B in rad/s.
    @type dw:                   float
    @keyword k_AB:              The rate of exchange from site A to B (rad/s).
    @type k_AB:                 float
    @keyword k_BA:              The rate of exchange from site B to A (rad/s).
    @type k_BA:                 float
    @keyword relax_time:        The total relaxation time period (in seconds).
    @type relax_time:           float
    @keyword inv_relax_time:    The inverse of the total relaxation time period (in inverse seconds).
    @type inv_relax_time:       float
    @keyword tcp:               The tau_CPMG times (1 / 4.nu1).
    @type tcp:                  numpy rank-1 float array
    @keyword back_calc:         The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:            numpy rank-1 float array
    @keyword num_points:        The number of points on the dispersion curve, equal to the length of the tcp and back_calc arguments.
    @type num_points:           int
    @keyword num_cpmg:          The array of numbers of CPMG blocks.
    @type num_cpmg:             numpy int16, rank-1 array
    """

    # The expansion factors (in numpy array form for all dispersion points).
    t3 = complex(0, 1)
    t4 = t3 * dw
    t5 = k_BA * k_BA
    t8 = 2.0 * t3 * k_BA * dw
    t10 = 2.0 * k_BA * k_AB
    t11 = dw * dw
    t14 = 2.0 * t3 * k_AB*dw
    t15 = k_AB * k_AB
    t17 = cmath.sqrt(t5 - t8 + t10 - t11 + t14 + t15)
    t21 = exp((-k_BA + t4 - k_AB + t17) * tcp/4.0)
    t22 = 1.0/t17
    t28 = exp((-k_BA + t4 - k_AB - t17) * tcp/4.0)
    t31 = t21 * t22 * k_AB - t28 * t22 * k_AB
    t33 = cmath.sqrt(t5 + t8 + t10 - t11 - t14 + t15)
    t34 = k_BA + t4 - k_AB + t33
    t37 = exp((-k_BA - t4 - k_AB + t33) * tcp/2.0)
    t39 = 1.0/t33
    t41 = k_BA + t4 - k_AB - t33
    t44 = exp((-k_BA - t4 - k_AB - t33) * tcp/2.0)
    t47 = t34 * t37 * t39/2.0 - t41 * t44 * t39/2.0
    t49 = k_BA - t4 - k_AB - t17
    t51 = t21 * t49 * t22
    t52 = k_BA - t4 - k_AB + t17
    t54 = t28 * t52 * t22
    t55 = -t51 + t54
    t60 = t37 * t39 * k_AB - t44 * t39 * k_AB
    t62 = t31 * t47 + t55 * t60/2.0
    t63 = 1.0/k_AB
    t68 = -t52 * t63 * t51/2.0 + t49 * t63 * t54/2.0
    t69 = t62 * t68/2.0
    t72 = t37 * t41 * t39
    t76 = t44 * t34 * t39
    t78 = -t34 * t63 * t72/2.0 + t41 * t63 * t76/2.0
    t80 = -t72 + t76
    t82 = t31 * t78/2.0 + t55 * t80/4.0
    t83 = t82 * t55/2.0
    t88 = t52 * t21 * t22/2.0 - t49 * t28 * t22/2.0
    t91 = t88 * t47 + t68 * t60/2.0
    t92 = t91 * t88
    t95 = t88 * t78/2.0 + t68 * t80/4.0
    t96 = t95 * t31
    t97 = t69 + t83
    t98 = t97 * t97
    t99 = t92 + t96
    t102 = t99 * t99
    t108 = t62 * t88 + t82 * t31
    t112 = numpy.sqrt(t98 - 2.0 * t99 * t97 + t102 + 4.0 * (t91 * t68/2.0 + t95 * t55/2.0) * t108)
    t113 = t69 + t83 - t92 - t96 - t112
    t115 = num_cpmg / 2.0
    t116 = power(t69/2.0 + t83/2.0 + t92/2.0 + t96/2.0 + t112/2.0, t115)
    t118 = 1.0/t112
    t120 = t69 + t83 - t92 - t96 + t112
    t122 = power(t69/2.0 + t83/2.0 + t92/2.0 + t96/2.0 - t112/2.0, t115)
    t127 = 1.0/t108
    t139 = 1.0/(k_AB + k_BA) * ((-t113 * t116 * t118/2.0 + t120 * t122 * t118/2.0) * k_BA + (-t113 * t127 * t116 * t120 * t118/2.0 + t120 * t127 * t122 * t113 * t118/2.0) * k_AB/2.0)

    # Calculate the initial and final peak intensities.
    intensity0 = pA
    intensity = real(t139) * exp(-relax_time * r20)

    # The magnetisation vector.
    Mx = intensity / intensity0

    # Calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential, and store it for each dispersion point.
    for i in range(num_points):
        if Mx[i] == 0.0:
            back_calc[i] = 1e99
        else:
            back_calc[i]= -inv_relax_time * log(Mx[i])
