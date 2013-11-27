###############################################################################
#                                                                             #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""The relaxation dispersion equations."""

# Python module imports.
from math import log, sqrt


def calc_two_point_r2eff(relax_time=None, I_ref=None, I=None):
    """Calculate the R2eff/R1rho value for the fixed relaxation time data.

    The formula is::

                  -1         / I1 \ 
        R2eff = ------- * ln | -- | ,
                relax_T      \ I0 /

    where relax_T is the fixed delay time, I0 is the reference peak intensity when relax_T is zero, and I1 is the peak intensity in a spectrum of interest.


    @keyword relax_time:    The fixed relaxation delay time in seconds.
    @type relax_time:       float
    @keyword I_ref:         The peak intensity in the reference spectrum.
    @type I_ref:            float
    @keyword I:             The peak intensity of interest.
    @type I:                float
    """

    # Calculate and return the value (avoiding integer division problems).
    return -1.0 / relax_time * log(float(I) / I_ref)


def calc_two_point_r2eff_err(relax_time=None, I_ref=None, I=None, I_ref_err=None, I_err=None):
    """Calculate the R2eff/R1rho error for the fixed relaxation time data.

    The formula is::

                                __________________________________
                      1        / / sigma_I1 \ 2     / sigma_I0 \ 2
        sigma_R2 = -------    /  | -------- |   +   | -------- |
                   relax_T  \/   \ I1(nu1)  /       \    I0    /

    where relax_T is the fixed delay time, I0 and sigma_I0 are the reference peak intensity and error when relax_T is zero, and I1 and sigma_I1 are the peak intensity and error in the spectrum of interest.


    @keyword relax_time:    The fixed relaxation delay time in seconds.
    @type relax_time:       float
    @keyword I_ref:         The peak intensity in the reference spectrum.
    @type I_ref:            float
    @keyword I:             The peak intensity of interest.
    @type I:                float
    @keyword I_ref_err:     The peak intensity error in the reference spectrum.
    @type I_ref_err:        float
    @keyword I_err:         The peak intensity error of interest.
    @type I_err:            float
    """

    # Calculate and return the value (avoiding integer division problems).
    return sqrt((I_ref_err / I_ref)**2 + (I_err / I)**2) / relax_time
