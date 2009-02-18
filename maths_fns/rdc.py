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

# Module docstring.
"""Module for the calculation of RDCs."""

# Python imports.
from numpy import dot, sum


def ave_rdc_5D(dj, vect, K, A, weights=None):
    """Calculate the average RDC for an ensemble set of XH bond vectors, using the 5D notation.

    This function calculates the average RDC for a set of XH bond vectors from a structural
    ensemble, using the 5D vector form of the alignment tensor.  The formula for this ensemble
    average RDC value is::

                    _K_
                  1 \ 
        <RDC_i> = -  >  RDC_ik (theta),
                  K /__
                    k=1

    where K is the total number of structures,  k is the index over the multiple structures, RDC_ik
    is the back-calculated RDC value for spin system i and structure k, and theta is the parameter
    vector consisting of the alignment tensor parameters {Axx, Ayy, Axy, Axz, Ayz}.  The
    back-calculated RDC is given by the formula::

        RDC_ik(theta) = (x**2 - z**2)Axx + (y**2 - z**2)Ayy + 2x.y.Axy + 2x.z.Axz + 2y.z.Ayz.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the unit
                        vector.
    @type vect:         numpy matrix
    @param K:           The total number of structures.
    @type K:            int
    @param A:           The 5D vector object.  The vector format is {Axx, Ayy, Axy, Axz, Ayz}.
    @type A:            numpy 5D vector
    @param weights:     The weights for each member of the ensemble.  The last weight is assumed to
                        be missing, and is calculated by this function.  Hence the length should be
                        one less than K.
    @type weights:      numpy rank-1 array
    @return:            The average RDC value.
    @rtype:             float
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # Averaging factor.
    if weights == None:
        c = 1.0 / K

    # Loop over the structures k.
    for k in xrange(K):
        # The weights.
        if weights != None:
            if k == K-1: 
                c = 1.0 - sum(weights, axis=0)
            else:
                c = weights[k]

        # Back-calculate the RDC.
        val = val + c * (vect[k,0]**2 - vect[k,2]**2)*A[0] + (vect[k,1]**2 - vect[k,2]**2)*A[1] + 2.0*vect[k,0]*vect[k,1]*A[2] + 2.0*vect[k,0]*vect[k,2]*A[3] + 2.0*vect[k,1]*vect[k,2]*A[4]

    # Return the average RDC.
    return dj * val


def ave_rdc_tensor(dj, vect, K, A, weights=None):
    """Calculate the ensemble average RDC, using the 3D tensor.

    This function calculates the average RDC for a set of XH bond vectors from a structural
    ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble
    average RDC value is::

                         _N_
                         \             T
        Dij(theta)  = dj  >  pc . mu_jc . Ai . mu_jc,
                         /__
                         c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - c is the index over the states or multiple structures,
        - theta is the parameter vector,
        - dj is the dipolar constant for spin j,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to
        1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - Ai is the alignment tensor.

    The dipolar constant is defined as::

        dj = 3 / (2pi) d',

    where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is
    associated with the alignment tensor and the pure dipolar constant in SI units is::

               mu0 gI.gS.h_bar
        d' = - --- ----------- ,
               4pi    r**3

    where:
        - mu0 is the permeability of free space,
        - gI and gS are the gyromagnetic ratios of the I and S spins,
        - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
        - r is the distance between the two spins.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the unit
                        vector.
    @type vect:         numpy matrix
    @param K:           The total number of structures.
    @type K:            int
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @param weights:     The weights for each member of the ensemble.  The last weight is assumed to
                        be missing, and is calculated by this function.  Hence the length should be
                        one less than K.
    @type weights:      numpy rank-1 array
    @return:            The average RDC value.
    @rtype:             float
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # Averaging factor.
    if weights == None:
        c = 1.0 / K

    # Loop over the structures k.
    for k in xrange(K):
        # The weights.
        if weights != None:
            if K > 1 and k == K-1: 
                c = 1.0 - sum(weights, axis=0)
            else:
                c = weights[k]

        # Back-calculate the RDC.
        val = val + c * dot(vect[k], dot(A, vect[k]))

    # Return the average RDC.
    return dj * val


def ave_rdc_tensor_dDij_dAmn(dj, vect, N, dAi_dAmn, weights=None):
    """Calculate the ensemble average RDC gradient element for Amn, using the 3D tensor.

    This function calculates the average RDC gradient for a set of XH bond vectors from a structural
    ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble
    average RDC gradient element is::

                          _N_
        dDij(theta)       \             T   dAi
        -----------  = dj  >  pc . mu_jc . ---- . mu_jc,
           dAmn           /__              dAmn
                          c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
        - n, the index over the second dimension of the alignment tensor n = {x, y, z},
        - c is the index over the states or multiple structures,
        - theta is the parameter vector,
        - Amn is the matrix element of the alignment tensor,
        - dj is the dipolar constant for spin j,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to
        1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - dAi/dAmn is the partial derivative of the alignment tensor with respect to element Amn.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the unit
                        vector.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param dAi_dAmn:    The alignment tensor derivative with respect to parameter Amn.
    @type dAi_dAmn:     numpy rank-2 3D tensor
    @param weights:     The weights for each member of the ensemble.  The last weight is assumed to
                        be missing, and is calculated by this function.  Hence the length should be
                        one less than N.
    @type weights:      numpy rank-1 array
    @return:            The average RDC gradient element.
    @rtype:             float
    """

    # Initial back-calculated RDC gradient.
    grad = 0.0

    # The populations.
    if weights == None:
        pc = 1.0 / N

    # Back-calculate the RDC gradient element.
    for c in xrange(N):
        # The weights.
        if weights != None:
            if N > 1 and c == N-1: 
                pc = 1.0 - sum(weights, axis=0)
            else:
                pc = weights[c]

        grad = grad + pc * dot(vect[c], dot(dAi_dAmn, vect[c]))

    # Return the average RDC gradient element.
    return dj * grad


def rdc_tensor(dj, mu, A):
    """Calculate the RDC, using the 3D alignment tensor.

    The RDC value is::

                               T
        Dij(theta)  = dj . mu_j . Ai . mu_j,

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - theta is the parameter vector,
        - dj is the dipolar constant for spin j,
        - mu_j i the unit vector corresponding to spin j,
        - Ai is the alignment tensor.

    The dipolar constant is defined as::

        dj = 3 / (2pi) d',

    where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is
    associated with the alignment tensor and the pure dipolar constant in SI units is::

               mu0 gI.gS.h_bar
        d' = - --- ----------- ,
               4pi    r**3

    where:
        - mu0 is the permeability of free space,
        - gI and gS are the gyromagnetic ratios of the I and S spins,
        - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
        - r is the distance between the two spins.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param mu:          The unit XH bond vector.
    @type mu:           numpy rank-1 3D array
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @return:            The RDC value.
    @rtype:             float
    """

    # Return the RDC.
    return dj * dot(mu, dot(A, mu))
